#!/usr/bin/env python
import json
import datetime
import pandas as pd
import re

NORMALIZE_FIELD_TABLE = json.load(open("../code/normalize_field_table.json"))
REMOVE_ERRANT_FOOTNOTES_TABLE = json.load(open("../code/remove_errant_footnotes_table.json"))

################################################################################
def normalize_fields(text, table, field):
	table_lookup = NORMALIZE_FIELD_TABLE[table]
	try:
		value_lookup = table_lookup[field]
	except KeyError:
		return text
	else:
		try:
			value = value_lookup[text]
		except KeyError:
			return text
		else:
			return value

################################################################################
def get_date_from_fname(f_name):
	raw_date = re.search(r'(\d+).txt', f_name).group(1)
	date = datetime.date(2000+int(raw_date[0:2]), int(raw_date[2:4]), int(raw_date[4:6]))
	return date


################################################################################
def get_table_name(line):
	try:
		table_line = re.search(r'\s+TABLE\s+[\w-]+.*', line).group()
		table_name = table_line.strip()
	except AttributeError:
		table_name = None
	return table_name


################################################################################
def normalize_page_text(page):
	# ignore unicode errors
	# i.e. remove superscript 3 symbols ('\xc2\xb3') by way of ignoring their errors
	# hopefully this doesn't have any undesirable side-effects
	page = re.sub("\xc2\xa0|\xc2\xb3", "", page)
	# split on line breaks, usually '\r\n' and rarely just '\n'
	lines = re.split(r'\r\n|\n', page)
	# get rid of pipe delimiters and divider lines
	lines = [re.sub(r'^ \|', '       ', line) for line in lines]
	lines = [re.sub(r'\|', '', line) for line in lines]
	lines = [re.sub(r'\s?_{5,}', '', line) for line in lines]
	# get rid of dollar signs and thousand commas
	lines = [re.sub(r'\$', '', line) for line in lines]
	lines = [re.sub(r'(\d),(\d)', r'\1\2', line) for line in lines]
	# normalize non-leading white space
	lines = [line[:6] + re.sub(r'\s{2,}', ' ', line[6:]) for line in lines]
	lines = [line.rstrip() for line in lines]
	# get rid of blank lines
	lines = [line for line in lines if line!='' and line!=' ']
	return lines


################################################################################
def get_footnote(line):
	footnote = re.search(r'^\s*(\d)\/(\w+.*)', line)
	if footnote:
		return [footnote.group(1), footnote.group(2)]
	return None


################################################################################
def parse_file(f_name, verbose=False):

	f = open(f_name, 'rb').read()

	raw_tables = re.split(r'(\s+TABLE\s+[\w-]+.*)', f)
	tables = []
	for raw_table in raw_tables[1:]:
		if re.search(r'\s+TABLE\s+[\w-]+.*', raw_table):
			table_name = raw_table
			continue
		raw_table = table_name + raw_table
		table = normalize_page_text(raw_table)
		tables.append(table)

	# file metadata
	date = get_date_from_fname(f_name)
	print 'INFO: parsing', f_name, '(', date, ')'

	dfs = {}
	for table in tables:
		table_index = tables.index(table)
		#if table_index != 1: continue
		dfs[table_index] = parse_table(table, date, verbose=verbose)

	return dfs

################################################################################
def parse_table(table, date, verbose=False):

	# table defaults
	indent = 0
	footnotes = {}
	index = surtype_index = type_index = subtype_index = used_index = -1
	type_indent = subtype_indent = -1
	type_ = subtype = None
	table_name = None

	# total hack for when the treasury decided to switch
	# which (upper or lower) line of two-line items gets the 0s
	# NOTE: THIS IS ONLY FOR TABLE I, BECAUSE OF COURSE
	if date > datetime.date(2013, 1, 3) or date < datetime.date(2012, 6, 1):
		two_line_delta = 1
	else:
		two_line_delta = -1

	parsed_table = []
	for line in table:
		#print '|' + line + '|'
		row = {}

		# a variety of date formats -- for your convenience
		row['date'] = date
		row['year'] = date.year
		row['month'] = date.month
		row['day'] = date.day
		row['year_month'] = datetime.date.strftime(date, '%Y-%m')
		row['weekday'] = datetime.datetime.strftime(date, '%A')

		# what's our line number? shall we bail out?
		index += 1
		if index <= used_index: continue

		indent = len(re.search(r'^\s*', line).group())

		# Rows that we definitely want to skip
		# empty or centered header rows
		if re.match(r'^\s{7,}', line): continue
		# page number rows
		page_number_match = re.search(r'\d+.*DAILY\s+TREASURY\s+STATEMENT.*PAGE:\s+(\d+)', line)
		if page_number_match:
			page_number = page_number_match.group(1)
			continue
		# catch rare exceptions to the above
		if re.search(r'DAILY\s+TREASURY\s+STATEMENT.*PAGE', line):
			continue
		# comment on statutory debt limit at end of Table III-C, and beyond
		if re.search(r'(As|Act) of [A-Z]\w+ \d+, \d+', line) and re.search(r'(statutory )*debt( limit)*', line):
			break
		# comment on whatever this is; above line may make this redundant
		if re.search(r'\s*Unamortized Discount represents|amortization is calculated daily', line, flags=re.IGNORECASE):
			break
		# comment about food stamp program euphemism
		if re.search(r'\s*The Food Stamp Program has been renamed', line, flags=re.IGNORECASE):
			break
		# final footer of file
		if re.search(r"\s+This statement summarizes\s+the United States Treasury's cash and debt", line):
			break
		# final footer of file -- above line should make this redundant! but just in case
		if re.search(r'\s+SOURCE:\s+Financial\s+Management', line):
			break
		# NOT IMPLEMENTED YET, WE SHOULD TRY TO FIX THE PARSER FIRST
		# # ignore errant footnotes:
		# if any([re.search(".*%s.*" % f, line) for f in REMOVE_ERRANT_FOOTNOTES_TABLE]):
		# 	break

		# skip table header rows
		if get_table_name(line):
			table_name = get_table_name(line)
			continue
		row['table'] = table_name

		# save footnotes for later assignment to their rows
		footnote = get_footnote(line)
		if footnote is not None:
			# while footnote does not end in valid sentence-ending punctuation...
			i = 1
			while not re.search(r'[.!?]$', footnote[1]):
				# get next line, if it exists
				try:
					next_line = table[index + i]
				except IndexError:
					break
				# and next line is not itself a new footnote...
				if not get_footnote(next_line):
					# add next line text to current footnote
					footnote[1] = ''.join([footnote[1], next_line])
					used_index = index + i
					i += 1
			# make our merged footnote hack official!
			footnotes[footnote[0]] = footnote[1]
			# if next line after footnote is not another footnote
			# it is most assuredly extra comments we don't need
			try:
				last_line = table[index + i]
			except IndexError:
				break
			if not get_footnote(last_line):
				break

		# note rows with footnote markers for later assignment
		if re.search(r'\d+\/', line):
			row['footnote'] = re.search(r'(\d+)\/', line).group(1)

		# separate digits and words
		digits = re.findall(r'(-{,1}\d+)', line)
		words = re.findall(r'\(\-\)|[()]|[^\W\d]+:?', line)
		# bug fix, to remove the govt's usage of 'r/' in front of numbers
		# to denote revised values
		text = ' '.join(word for word in words if word != 'r')

		# get type row
		if len(digits) == 0 and text.endswith(':') and indent == 1:
			type_ = text[:-1]
			type_indent = indent
			type_index = index
			continue
		elif indent <= type_indent:
			type_ = None
		row['type'] = type_

		# get subtype row
		if len(digits) == 0 and text.endswith(':'):
			subtype = text[:-1]
			subtype_indent = indent
			subtype_index = index
			continue
		if index == subtype_index + 1: pass # maybe unnecessary
		elif indent <= subtype_indent:
			subtype = None
		row['subtype'] = subtype

		# get and merge two-line rows
		if len(digits) == 0 and not text.endswith(':'):
			if two_line_delta == 1 or not re.search(r'TABLE I\s', row.get('table', '')):
				try:
					next_line = table[index + 1]
					# check for footnotes, then note and erase them if present!
					if re.search(r'\d+\/', next_line):
						row['footnote'] = re.search(r'(\d+)\/', next_line).group(1)
						next_line = re.sub(r'\d+\/', '', next_line)
					next_digits = re.findall(r'(\d+)', next_line)
					next_words = re.findall(r'[^\W\d]+:?', next_line)
					if len(next_digits) != 0:
						text = text + ' ' + ' '.join(next_words)
						digits = next_digits
						used_index = index + 1
				except IndexError: pass
			elif two_line_delta == -1 and re.search(r'TABLE I\s', row.get('table', '')):
				try:
					prev_line = table[index - 1]
					prev_digits = re.findall(r'(\d+)', prev_line)
					prev_words = re.findall(r'[^\W\d]+:?', prev_line)
					if len(prev_digits) != 0:
						text = ' '.join(prev_words) + ' ' + text
						digits = prev_digits
						get_rid_of_prev_line = parsed_table.pop()
				except IndexError: pass


		#print len(digits), '||', digits
		# skip table annotations that aren't footnotes
		# this is a band-aid at best, sorry folks
		if len(digits) == 0: continue

		row['is_total'] = int('total' in text.lower())

		if re.search(r'TABLE I\s|TABLE III-C', row.get('table', '')):
			try:
				if re.search(r'TABLE I\s', row.get('table', '')):
					row['account_raw'] = text
					row['account'] = normalize_fields(text, 't1', 'account')
				elif re.search(r'TABLE III-C', row.get('table', '')):
					try:
						row['item_raw'] = text
						row['item'] = normalize_fields(text, 't3c', 'item')
					except:
						if verbose is True:
							print 'WARNING:', line
				row['close_today'] = digits[-4]
				row['open_today'] = digits[-3]
				row['open_mo'] = digits[-2]
				row['open_fy'] = digits[-1]
			except:
				if verbose is True:
					print 'WARNING:', line
		elif re.search(r'TABLE II\s', row.get('table', '')):
			try:
				row['item_raw'] = text
				row['item'] = normalize_fields(text, 't2', 'item')
				row['today'] = digits[-3]
				row['mtd'] = digits[-2]
				row['fytd'] = digits[-1]
				# tweak column names
				row['account'] = row['type']
				# this is a hack, deal with it :-/
				row['type'] = 'deposit'
				if int(page_number) == 3:
					row['type'] = 'withdrawal'
				if row.get('subtype'):
					subtype = row['subtype']
					row['subitem'] = row['item']
					row['subitem_raw'] = row['item_raw']
					row['item'] = subtype
					row.pop('subtype')
					row.pop('item_raw')
			except:
				if verbose is True:
					print 'WARNING:', line
		elif re.search(r'TABLE III-A', row.get('table', '')):
			try:
				row['item_raw'] = text
				row['item'] = normalize_fields(text, "t3a", 'item')
				row['today'] = digits[-3]
				row['mtd'] = digits[-2]
				row['fytd'] = digits[-1]
				if row.get('subtype'):
					subtype = row['subtype']
					row['subitem'] = row['item']
					row['subitem_raw'] = row['item_raw']
					row['item'] = subtype
					row.pop('subtype')
					row.pop('item_raw')
			except:
				if verbose is True:
					print 'WARNING:', line
		elif re.search(r'TABLE III-B', row.get('table', '')):
			try:
				row['item_raw'] = text
				row['item'] = normalize_fields(text, "t3b", 'item')
				row['today'] = digits[-3]
				row['mtd'] = digits[-2]
				row['fytd'] = digits[-1]
				if row.get('subtype'):
					subtype = row['subtype']
					row['subitem'] = row['item']
					row['subitem_raw'] = row['item_raw']
					row['item'] = subtype
					row.pop('subtype')
					row.pop('item_raw')
			except:
				if verbose is True:
					print 'WARNING:', line
		elif re.search(r'TABLE IV', row.get('table', '')):
			try:
				row['classification_raw'] = text
				row['classification'] = normalize_fields(text, 't4', 'classification')
				row['today'] = digits[-3]
				row['mtd'] = digits[-2]
				row['fytd'] = digits[-1]
			except:
				if verbose is True:
					print 'WARNING:', line
		elif re.search(r'TABLE VI', row.get('table', '')):
			try:
				row['classification_raw'] = text
				row['classification'] = normalize_fields(text, 't6', 'classification')
				row['today'] = digits[-3]
				row['mtd'] = digits[-2]
				row['fytd'] = digits[-1]
			except:
				if verbose is True:
					print 'WARNING:', line
		elif re.search(r'TABLE V\s', row.get('table', '')):
			try:
				row['balance_transactions'] = text
				row['depositary_type_a'] = digits[-4]
				row['depositary_type_b'] = digits[-3]
				row['depositary_type_c'] = digits[-2]
				row['total'] = digits[-1]
			except:
				if verbose is True:
					print 'WARNING:', line

		parsed_table.append(row)

	# assign footnotes to rows
	# and split table III-a by surtype
	for row in parsed_table:
		if row.get('footnote'):
			row['footnote'] = footnotes.get(row['footnote'])
		if row.get('item'):
			if row['item'].lower().strip() == 'total issues':
				surtype_index = parsed_table.index(row)
				row['surtype'] = 'issue'

	# after-the-fact surtype assignment
	if surtype_index != -1:
		for row in parsed_table[:surtype_index]:
			row['surtype'] = 'issue'
		for row in parsed_table[surtype_index + 1:]:
			row['surtype'] = 'redemption'

	# create data frame from table list of row dicts
	df = pd.DataFrame(parsed_table)

	# and pretty them up
	if re.search(r'TABLE I\s', row.get('table', '')):
		df = df.reindex(columns=['table', 'date', 'year_month', 'year', 'month', 'day', 'weekday', 'account', 'account_raw', 'is_total', 'close_today', 'open_today', 'open_mo', 'open_fy', 'footnote'])
	elif re.search(r'TABLE II\s', row.get('table', '')):
		df = df.reindex(columns=['table', 'date', 'year_month', 'year', 'month', 'day', 'weekday', 'account', 'account_raw', 'type', 'item', 'item_raw', 'subitem', 'subitem_raw', 'is_total', 'today', 'mtd', 'fytd', 'footnote'])
	elif re.search(r'TABLE III-A', row.get('table', '')):
		df = df.reindex(columns=['table', 'date', 'year_month', 'year', 'month', 'day', 'weekday', 'surtype', 'type', 'item', 'item_raw', 'subitem', 'subitem_raw', 'is_total', 'today', 'mtd', 'fytd', 'footnote'])
	elif re.search(r'TABLE III-B', row.get('table', '')):
		df = df.reindex(columns=['table', 'date', 'year_month', 'year', 'month', 'day', 'weekday', 'type', 'item', 'item_raw', 'subitem', 'subitem_raw', 'is_total', 'today', 'mtd', 'fytd', 'footnote'])
	elif re.search(r'TABLE III-C', row.get('table', '')):
		df = df.reindex(columns=['table', 'date', 'year_month', 'year', 'month', 'day', 'weekday', 'type', 'item', 'item_raw', 'is_total', 'close_today', 'open_today', 'open_mo', 'open_fy', 'footnote'])
	elif re.search(r'TABLE IV|TABLE VI', row.get('table', '')):
		df = df.reindex(columns=['table', 'date', 'year_month', 'year', 'month', 'day', 'weekday', 'type', 'classification', 'classification_raw', 'is_total', 'today', 'mtd', 'fytd', 'footnote'])
	elif re.search(r'TABLE V\s', row.get('table', '')):
		df = df.reindex(columns=['table', 'date', 'year_month', 'year', 'month', 'day', 'weekday', 'type', 'balance_transactions', 'is_total', 'depositary_type_a', 'depositary_type_b', 'depositary_type_c', 'total', 'footnote'])

	return df

# BJD: Does this function serve a purpose...?
def strip_table_name(table_name):
    return re.sub('[^a-zA-Z]*$', '', table_name)
