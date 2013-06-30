#!/usr/bin/env python

import datetime
import download_fms_fixies
import os
import pandas as pd
import pandas.io.sql
import parse_fms_fixies
import re
import sqlite3
import sys

# script must be run from fms_parser/code directory
if not os.path.split(os.getcwd())[-1] == 'code':
	if os.path.split(os.getcwd())[-1] == 'fms_parser':
		os.chdir('code')
		print '\n*INFO: current working directory set to', os.getcwd()
	else:
		raise Exception('This script must be run from the fms_parser/code directory!')

# auto-make data directories, if not present
FIXIE_DIR = os.path.join('..', 'data', 'fixie')
DAILY_CSV_DIR = os.path.join('..', 'data', 'daily_csv')
LIFETIME_CSV_DIR = os.path.join('..', 'data', 'lifetime_csv')
os.system('mkdir -pv ' + FIXIE_DIR)
os.system('mkdir -pv ' + DAILY_CSV_DIR)
os.system('mkdir -pv ' + LIFETIME_CSV_DIR)

## DOWNLOAD! ##################################################################
# test for existence of downloaded fixies
test_fixies = sorted([f for f in os.listdir(FIXIE_DIR) if f.endswith('.txt')])
# if none, start from THE BEGINNING
if len(test_fixies) == 0:
	start_date = datetime.date(2005, 6, 9)
# else start from last available fixie date
else:
	start_date = parse_fms_fixies.get_date_and_day(test_fixies[-1])[0]
# always end with today
end_date = datetime.date.today()

# download all teh fixies!
fnames = download_fms_fixies.download_fixies(start_date, end_date)

# check all downloaded fixies against all parsed csvs
downloaded_files = set([fixie.split('.')[0] for fixie in os.listdir(FIXIE_DIR)
	if fixie.endswith('.txt')])
def parsed_files():
	return set([csv.split('_')[0] for csv in os.listdir(DAILY_CSV_DIR) if csv.endswith('.csv')])


## PARSE! #####################################################################
# fixies that have not yet been parsed into csvs
new_files = sorted(list(downloaded_files.difference(parsed_files())))

# parse all teh fixies!
for f in new_files:
	fname = os.path.join(FIXIE_DIR, f+'.txt')
	#print '\n', fname
	dfs = parse_fms_fixies.parse_file(fname, verbose=False)

	# each table for each date stored in separate csv files
	for df in dfs.values():
		try:
			t_name = df.ix[0,'table']
			t_name_match = re.search(r'TABLE [\w-]+', t_name)
			t_name_short = re.sub(r'-| ', '_', t_name_match.group().lower())
		except Exception as e:
			print '***ERROR: tables failed to parsed!', e
			# go on
			continue

		daily_csv = os.path.join(DAILY_CSV_DIR, f.split('.')[0]+'_'+t_name_short+'.csv')
		df.to_csv(daily_csv, index=False, header=True, encoding='utf-8', na_rep='')

# iterate over all fms tables
for i in ['i', 'ii', 'iii_a', 'iii_b', 'iii_c', 'iv', 'v', 'vi']:

	# create the lifetime csv files it they don't exist
	lifetime_csv = os.path.join(LIFETIME_CSV_DIR, 'table_'+str(i)+'.csv')

	# if it doesn't exist
	if not os.path.isfile(lifetime_csv):
		lifetime = open(lifetime_csv, 'ab')
		# add the header
		lifetime.write(open(os.path.join(DAILY_CSV_DIR, list(parsed_files())[0]+'_table_'+str(i)+'.csv')).readline())
		lifetime.close()

	# append new csvs to lifetime csvs
	for f in new_files:

		# we have no idea why it's giving us a blank file
		if len(f) == 0: continue

		daily_csv = os.path.join(DAILY_CSV_DIR, f.split('.')[0]+'_table_'+str(i)+'.csv')
		if not os.path.isfile(daily_csv): continue

		lifetime = open(lifetime_csv, 'ab')
		daily = open(daily_csv, 'rb')

		daily.readline() # burn header
		for line in daily:
			lifetime.write(line)
		daily.close()


## SQL-IZE! ###################################################################
TABLES = [
	{
		'raw-table': 'i',
		'new-table': 't1',
	},
	{
		'raw-table': 'ii',
		'new-table': 't2',
	},
	{
		'raw-table': 'iii_a',
		'new-table': 't3a',
	},
	{
		'raw-table': 'iii_b',
		'new-table': 't3b',
	},
	{
		'raw-table': 'iii_c',
		'new-table': 't3c',
	},
	{
		'raw-table': 'iv',
		'new-table': 't4',
	},
	{
		'raw-table': 'v',
		'new-table': 't5',
	},
	{
		'raw-table': 'vi',
		'new-table': 't6',
	},
]

connection = sqlite3.connect(os.path.join('..', 'data', 'treasury_data.db'))
connection.text_factory = str # bad, but pandas doesn't work otherwise

for table in TABLES:
	df = pandas.read_csv(os.path.join('..', 'data', 'lifetime_csv', 'table_%s.csv' % table['raw-table']))

	# WARNING SERIOUS HACKS FOLLOW #
	# FILTER OUT TABLE 5 AFTER  2012-04-02 - HACK BUT WORKS FOR NOW #
	if table['new-table']=="t5":
		print "HACK: filtering out invalid dates for TABLE V"
		table_v_end = datetime.date(2012, 4, 2)
		df.date = df.date.apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").date())
		df = df[df.date < table_v_end]

	pandas.io.sql.write_frame(df, '_table_%s' % table['raw-table'], connection)
	connection.execute('DROP TABLE IF EXISTS "%s";' % table['new-table'])
	connection.execute('ALTER TABLE "_table_%s" RENAME TO "%s";' % (table['raw-table'], table['new-table']))

# Commit
connection.commit()


## CELEBRATE! #################################################################
csv_txt = r"""
	  ,----..    .--.--.
	 /   /   \  /  /    '.       ,---.
	|   :     :|  :  /`. /      /__./|
	.   |  ;. /;  |  |--`  ,---.;  ; |
	.   ; /--` |  :  ;_   /___/ \  | |
	;   | ;     \  \    `.\   ;  \ ' |
	|   : |      `----.   \\   \  \: |
	.   | '___   __ \  \  | ;   \  ' .
	'   ; : .'| /  /`--'  /  \   \   '
	'   | '/  :'--'.     /    \   `  ;
	|   :    /   `--'---'      :   \ |
	 \   \ .'                   '---"
	  `---`
"""
soundsystem_txt = r"""
.-. .-. . . . . .-. .-. . . .-. .-. .-. .  .
`-. | | | | |\| |  )`-.  |  `-.  |  |-  |\/|
`-' `-' `-' ' ` `-' `-'  `  `-'  '  `-' '  `
"""
welcome_msg = r"""
Everything you just downloaded is in the data/ directory.
The raw files are in data/fixie.
They were parsed and converted to csvs in the data/daily_csv directory.
These are combined by table in the data/lifetime_csv directory.
Those tables were made into a SQLite database at data/treasury_data.db, which you can load using your favorite SQLite viewer.
If you have any questions, check out http://treasury.io for usage and a link to the support Google Group.
"""
print csv_txt
print soundsystem_txt
print '*http://csvsoundsystem.com/'
print welcome_msg
