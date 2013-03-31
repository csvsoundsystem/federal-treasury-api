
import collections
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pprint import pprint
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
	try:
		footnote_match = re.search(r'^\s?(\d)\/(.*)', line)
		footnote = [footnote_match.group(1), footnote_match.group(2)]
	except AttributeError:
		footnote = None
	return footnote

################################################################################
def parse_file(f_name):

	f = open(f_name, 'r').read()
	raw_pages = re.split(r'\d.*DAILY TREASURY STATEMENT.*PAGE:\s+\d\s{2}', f)
	pages = []
	for raw_page in raw_pages:
		page = normalize_page_text(raw_page)
		pages.append(page)

	# file metadata
	date = get_date_and_day(f_name)[0]
	day = get_date_and_day(f_name)[1]
	print f_name
	print date, ',', day

	dfs = {}
	for page in pages[1:]:
		page_index = pages.index(page)
		dfs[page_index] = parse_page(page, page_index, date, day)

	return dfs

################################################################################
def parse_page(page, page_index, date, day):

	# page defaults
	indent = 0
	footnotes = {}
	surtype_index = -1; type_index = -1; subtype_index = -1; used_index = -1
	type_indent = -1; subtype_indent = -1
	type_ = None; subtype = None
	table_name = None
	table_name_2 = None

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
		
		row['date'] = date
		row['day'] = day
		
		index = page.index(line)
		if index == used_index : continue
		indent = len(re.search(r'^\s*', line).group())
		
		# skip table header rows
		if re.match(r'\s{7,}', line): continue
		if get_table_name(line):
			table_name = get_table_name(line)
			continue
		row['table'] = table_name
		
		# save footnotes for later assignment to their rows
		if get_footnote(line):
			footnote = get_footnote(line)
			footnotes[footnote[0]] = footnote[1]
			continue
		# note rows with footnotes for later assignment
		if re.search(r'\d\/ ', line):
			row['footnote'] = re.search(r'(\d)\/ ', line).group(1)
		
		# separate digits and words
		digits = re.findall(r'(\d+)', line)
		words = re.findall(r'[^\W\d]+:?', line)
		text = ' '.join(words)
		
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
				print "WARNING:", line
		elif page_index in [4, 5]:
			try:
				row['item'] = text
				row['today'] = digits[-3]
				row['mtd'] = digits[-2]
				row['fytd'] = digits[-1]
			except:
				print "WARNING:", line
		elif page_index in [7,8]:
			try:
				row['classification'] = text
				row['today'] = digits[-3]
				row['mtd'] = digits[-2]
				row['fytd'] = digits[-1]
			except:
				print "WARNING:", line
			
		table.append(row)

	# assign footnotes to rows
	for row in table:
		try:
			row['footnote'] = footnotes[row['footnote']]
		except KeyError: pass
		try:
			if row['item'].lower().strip() == 'total issues':
				surtype_index = table.index(row)
				row['surtype'] = 'issue'
		except KeyError: pass

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
		df = df.reindex(columns=['table', 'date', 'day', 'account', 'is_total', 'close_today', 'open_today', 'open_mo', 'open_fy', 'footnote'])
	if page_index in [2,3]:
		df = df.reindex(columns=['table', 'date', 'day', 'account', 'type', 'subtype', 'item', 'is_total', 'today', 'mtd', 'fytd', 'footnote'])
	elif page_index in [4,5]:
		df = df.reindex(columns=['table', 'date', 'day', 'surtype', 'type', 'subtype', 'item', 'is_total', 'today', 'mtd', 'fytd', 'footnote'])
	elif page_index == 6:
		df = df.reindex(columns=['table', 'date', 'day', 'type', 'item', 'is_total', 'close_today', 'open_today', 'open_mo', 'open_fy', 'footnote'])
	elif page_index in [7,8]:
		df = df.reindex(columns=['table', 'date', 'day', 'type', 'classification', 'is_total', 'today', 'mtd', 'fytd', 'footnote'])
	
	return df

