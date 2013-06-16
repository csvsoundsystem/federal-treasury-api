
import collections
import datetime
import pandas as pd
import re
import StringIO

################################################################################
def get_date_and_day(f_name):
	raw_date = re.search(r'(\d+).txt', f_name).group(1)
	date = datetime.date(2000+int(raw_date[0:2]), int(raw_date[2:4]), int(raw_date[4:6]))
	day = datetime.datetime.strftime(date, '%A')
	return date, day

################################################################################
def get_table_name(line):
	try:
		table_line = re.search(r'\s+TABLE.*', line).group()
		table_name = table_line.strip()
	except AttributeError:
		table_name = None
	return table_name

################################################################################
def normalize_page_text(page):
	# ignore unicode errors
	# i.e. remove superscript 3 symbols ('\xc2\xb3') by way of ignoring their errors
	# hopefully this doesn't have any undesirable side-effects
	page = unicode(page, errors='ignore')
	# split on line breaks
	lines = re.split(r'\r\n', page)
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
	raw_pages = re.split(r'\d.*DAILY TREASURY STATEMENT.*PAGE:\s+\d\s{2}', f)
	pages = []
	for raw_page in raw_pages:
		page = normalize_page_text(raw_page)
		pages.append(page)

	# file metadata
	date = get_date_and_day(f_name)[0]
	day = get_date_and_day(f_name)[1]
	print 'INFO: parsing', f_name, '(', date, ')'

	dfs = {}
	for page in pages[1:]:
		page_index = pages.index(page)
		dfs[page_index] = parse_page(page, page_index, date, day, verbose=verbose)

	return dfs

################################################################################
def parse_page(page, page_index, date, day, verbose=False):

	# page defaults
	indent = 0
	footnotes = {}
	surtype_index = -1; type_index = -1; subtype_index = -1; used_index = -1
	type_indent = -1; subtype_indent = -1
	type_ = None; subtype = None
	table_name = None

	# total hack for when the treasury decided to switch
	# which (upper or lower) line of two-line items gets the 0s
	# NOTE: THIS IS ONLY FOR TABLE I, BECAUSE OF COURSE
	if date > datetime.date(2013, 1, 3) or date < datetime.date(2012, 6, 1):
		two_line_delta = 1
	else:
		two_line_delta = -1

	table = []
	for line in page:
		#print line
		row = {}

		# a variety of date formats -- for your convenience
		row['date'] = date
		row['year'] = date.year
		row['month'] = date.month
		row['year-month'] = datetime.date.strftime(date, '%Y-%m')
		row['day'] = day

		index = page.index(line)
		if index <= used_index : continue
		indent = len(re.search(r'^\s*', line).group())

		# skip table header rows
		if re.match(r'\s{7,}', line): continue
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
					next_line = page[index + i]
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
				last_line = page[index + i]
			except IndexError:
				break
			if not get_footnote(last_line):
				break

		# note rows with footnote markers for later assignment
		if re.search(r'\d+\/', line):
			row['footnote'] = re.search(r'(\d+)\/', line).group(1)

		# separate digits and words
		digits = re.findall(r'(-{,1}\d+)', line)
		words = re.findall(r'[^\W\d]+:?', line)
		# bug fix, to remove the govt's arbitrary usage of 'r/' instead of '$'
		# in front of particular dollar amounts
		text = ' '.join(word for word in words if word != 'r')
		#text = ' '.join(words)

		# get type row
		if len(digits) == 0 and text.endswith(':') and indent == 1:
			type_ = text[:-1]
			type_indent = indent
			type_index = index
			continue
		if index == type_index + 1: pass
		elif indent <= type_indent:
			type_ = None
		row['type'] = type_

		# get subtype row
		if len(digits) == 0 and text.endswith(':'):
			subtype = text[:-1]
			subtype_indent = indent
			subtype_index = index
			continue
		if index == subtype_index + 1: pass
		elif indent <= subtype_indent:
			subtype = None
		row['subtype'] = subtype

		# get and merge two-line rows
		if len(digits) == 0 and not text.endswith(':'):
			if two_line_delta == 1 or page_index != 1:
				try:
					next_line = page[index + 1]
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
			elif two_line_delta == -1 and page_index == 1:
				try:
					prev_line = page[index - 1]
					prev_digits = re.findall(r'(\d+)', prev_line)
					prev_words = re.findall(r'[^\W\d]+:?', prev_line)
					if len(prev_digits) != 0:
						text = ' '.join(prev_words) + ' ' + text
						digits = prev_digits
						get_rid_of_prev_line = table.pop()
				except IndexError: pass

		# skip table annotations that aren't footnotes
		# this is a band-aid at best, sorry folks
		if len(digits) == 0: continue

		row['is_total'] = int('total' in text.lower())

		if page_index in [1, 6]:
			try:
				if page_index == 1:
					row['account'] = text
				elif page_index == 6:
					try: row['item'] = text
					except: print line
				row['close_today'] = digits[-4]
				row['open_today'] = digits[-3]
				row['open_mo'] = digits[-2]
				row['open_fy'] = digits[-1]
			except:
				if verbose is True:
					print "WARNING:", line
		elif page_index in [2, 3]:
			try:
				row['item'] = text
				row['today'] = digits[-3]
				row['mtd'] = digits[-2]
				row['fytd'] = digits[-1]
				# tweak column names
				row['account'] = row['type']
				if page_index == 2:
					row['type'] = 'deposit'
				elif page_index == 3:
					row['type'] = 'withdrawal'
			except:
				if verbose is True:
					print "WARNING:", line
		elif page_index in [4, 5]:
			try:
				row['item'] = text
				row['today'] = digits[-3]
				row['mtd'] = digits[-2]
				row['fytd'] = digits[-1]
			except:
				if verbose is True:
					print "WARNING:", line
		elif page_index in [7,8]:
			try:
				row['classification'] = text
				row['today'] = digits[-3]
				row['mtd'] = digits[-2]
				row['fytd'] = digits[-1]
			except:
				if verbose is True:
					print "WARNING:", line

		table.append(row)

	# assign footnotes to rows
	# and split table III-a by surtype
	for row in table:
		if row.get('footnote'):
			row['footnote'] = footnotes.get(row['footnote'])
		if row.get('item'):
			if row['item'].lower().strip() == 'total issues':
				surtype_index = table.index(row)
				row['surtype'] = 'issue'

	# after-the-fact surtype assignment
	if surtype_index != -1:
		for row in table[:surtype_index]:
			row['surtype'] = 'issue'
		for row in table[surtype_index + 1:]:
			row['surtype'] = 'redemption'

	# create data frame from table list of row dicts
	df = pd.DataFrame(table)

	# and pretty them up
	if page_index == 1:
		df = df.reindex(columns=['table', 'date', 'year-month', 'year', 'month', 'day', 'account', 'is_total', 'close_today', 'open_today', 'open_mo', 'open_fy', 'footnote'])
	if page_index in [2,3]:
		df = df.reindex(columns=['table', 'date', 'year-month', 'year', 'month', 'day', 'account', 'type', 'subtype', 'item', 'is_total', 'today', 'mtd', 'fytd', 'footnote'])
	elif page_index in [4,5]:
		df = df.reindex(columns=['table', 'date', 'year-month', 'year', 'month', 'day', 'surtype', 'type', 'subtype', 'item', 'is_total', 'today', 'mtd', 'fytd', 'footnote'])
	elif page_index == 6:
		df = df.reindex(columns=['table', 'date', 'year-month', 'year', 'month', 'day', 'type', 'item', 'is_total', 'close_today', 'open_today', 'open_mo', 'open_fy', 'footnote'])
	elif page_index in [7,8]:
		df = df.reindex(columns=['table', 'date', 'year-month', 'year', 'month', 'day', 'type', 'classification', 'is_total', 'today', 'mtd', 'fytd', 'footnote'])

	# table: string
	# date: string, in standard YYYY-MM-DD format
	# day: string, full name of day
	# account: string, name of associated account
	# surtype: string, e.g. 'issue' or 'redemption'
	# type: string, e.g. 'deposit' or 'withdrawal'
	# subtype: string, e.g. 'deposits by states' or 'other withdrawals'
	# classification: string, class of taxes
	# item: string, name of line item, e.g. 'Energy Department programs' or 'Postal service'
	# account: string
	# is_total: int, 0 if False (is not a total) and 1 if True (is a total)
	# today: int
	# mtd: int, month-to-date
	# ytd: int, year-to-date
	# fytd: int, fiscal-year-to-date
	# close_today: int
	# open_today: int
	# open_mo: int
	# open_fy: int
	# footnote: string

	return df

def strip_table_name(table_name):
    return re.sub('[^a-zA-Z]*$', '', table_name)
