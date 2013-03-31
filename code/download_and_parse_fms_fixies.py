#!/usr/bin/env python

import download_fms_fixies
import parse_fms_fixies_2
import datetime
import os
import sys
import pandas as pd

if not os.path.split(os.getcwd())[-1] == 'code':
	raise Exception('This file has to be run from the "code" directory!')

FIXIE_DIR = '../data/fixie/'
DAILY_CSV_DIR = '../data/daily_csv/'
LIFETIME_CSV_DIR = '../data/lifetime_csv/'

# test for existence of fixies; if none, start from THE BEGINNING
test_fixies = [f for f in os.listdir(FIXIE_DIR) if '.txt' in f]
if len(test_fixies) == 0:
	start_date = datetime.date(2005, 6, 9)
else:
	start_date = datetime.date.today() - datetime.timedelta(days=7)
end_date = datetime.date.today()

# download all teh fixies!
fnames = download_fms_fixies.download_fixies(start_date, end_date)

# check all fixies against all parsed csvs
downloaded_files = set([fixie.split('.')[0] for fixie in os.listdir(FIXIE_DIR)
	if fixie != '.DS_Store'])
def parsed_files():
	return set([csv.split('_')[0] for csv in os.listdir(DAILY_CSV_DIR)])

# fixies that have not been parsed into csvs
new_files = list(downloaded_files.difference(parsed_files()))
# PARSE THEM
for f in new_files:
	fname = '../data/fixie/' + f + '.txt'
	print '\n', fname
	dfs = parse_fms_fixies_2.parse_file(fname)

	for i, df in dfs.items():
		daily_csv = os.path.join(DAILY_CSV_DIR, f.split('.')[0]+'_t'+str(i)+'.csv')
		df.to_csv(daily_csv,
			index=False, header=True, encoding='utf-8', na_rep='NA')

# iterate over all fms tables
for i in range(1,9):

	# create the lifetime csv files it they don't exist
	lifetime_csv = os.path.join(LIFETIME_CSV_DIR, 'table_'+str(i)+'.csv')

	# if it doesn't exist
	if not os.path.isfile(lifetime_csv):
		lifetime = open(lifetime_csv, 'a')
		# add the header
		lifetime.write(open(parsed_files()[0]).readline())
		lifetime.close()

	# append new csvs to lifetime csvs
	for f in new_files:

		daily_csv = os.path.join(DAILY_CSV_DIR, f.split('.')[0]+'_t'+str(i)+'.csv')

		lifetime = open(lifetime_csv, 'a')
		daily = open(daily_csv, 'r')

		daily.readline() # burn header
		for line in daily:
			lifetime.write(line)
		daily.close()








