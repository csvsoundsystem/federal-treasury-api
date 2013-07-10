#!/usr/bin/env python
import codecs
import datetime
import os
import pandas as pd
import requests
import sys

BASE_URL = 'https://www.fms.treas.gov/fmsweb/viewDTSFiles'
SAVE_DIR = os.path.join('..', 'data', 'fixie')
HOLIDAYS = [datetime.datetime.strptime(d, '%Y%m%d').date() for d in [
	'20050117', '20050221', '20050530', '20050704', '20050905', '20051010', '20051111', '20051124', '20051226',
	'20060102', '20060116', '20060220', '20060529', '20060704', '20060904', '20061009', '20061110', '20061123', '20061225',
	'20070101', '20070115', '20070219', '20070528', '20070704', '20070903', '20071008', '20071112', '20071122', '20071225',
	'20080101', '20080121', '20080218', '20080526', '20080704', '20080901', '20081013', '20081111', '20081127', '20081225',
	'20090101', '20090119', '20090216', '20090525', '20090703', '20090907', '20091012', '20091111', '20091126', '20091225',
	'20100101', '20100118', '20100215', '20100531', '20100705', '20100906', '20101011', '20101111', '20101125', '20101224',
	'20101231', '20110117', '20110221', '20110530', '20110704', '20110905', '20111010', '20111111', '20111124', '20111226',
	'20120102', '20120116', '20120220', '20120528', '20120704', '20120903', '20121008', '20121112', '20121122', '20121225',
	'20130101', '20130121', '20130218', '20130527', '20130704', '20131014', '20131111', '20131128', '20131225', '20130709',
	]]

################################################################################
def check_dates(start_date, end_date):
	# fixie files not available before this date
	# PDFs *are* available, for the brave soul who wants to parse them
	earliest_date = datetime.date(2005, 6, 9)
	if start_date < earliest_date:
		print '\n**WARNING:', start_date, 'before earliest available date (',
		print str(earliest_date), ')'
		print '... setting start_date to', str(earliest_date)
		start_date = earliest_date
	if start_date > end_date:
		temp = start_date
		start_date = end_date
		end_date = temp

	return start_date, end_date

################################################################################
def generate_date_range(start_date, end_date):
	start_date, end_date = check_dates(start_date, end_date)
	dates = []
	td = datetime.timedelta(days=1)
	current_date = start_date
	while current_date <= end_date:
		dates.append(current_date)
		current_date += td
	return dates

################################################################################
def remove_weekends_and_holidays(all_dates):
	good_dates = [date for date in all_dates
				  if datetime.datetime.strftime(date, '%A') not in ['Saturday', 'Sunday']
				  and date not in HOLIDAYS]
	return good_dates

################################################################################
def request_fixie(fname):
	response = requests.get(BASE_URL,
							params={'dir': 'a',
									'fname': fname}
							)
	if response.status_code == 200:
		return response.text
	# check in working directory instead
	else:
		response = requests.get(BASE_URL,
						params={'dir': 'w',
								'fname': fname}
						)
		if response.status_code == 200:
			return response.text
		else:
			return None

################################################################################
def request_all_fixies(fnames):

	for fname in reversed(fnames):
		alt_fnames = [fname]
		alt_fnames.extend([fname[:-5] + i +'.txt' for i in ['1', '2', '3']])
		for alt_fname in alt_fnames:
			fixie = request_fixie(alt_fname)
			if fixie:
				print 'INFO: saving', os.path.join(SAVE_DIR, alt_fname)
				f = codecs.open(os.path.join(SAVE_DIR, alt_fname), 'wb', 'utf-8')
				f.write(fixie)
				f.close()
				break

		if fixie is None:
			print 'WARNING:', fname, '(',
			print str(datetime.datetime.strptime(fname[:6], '%y%m%d').date()),
			print ')', 'not available'

	return fnames


################################################################################
def download_fixies(start_date, end_date=None):
	start_date = datetime.datetime.strptime(str(start_date), '%Y-%m-%d').date()
	if end_date:
		end_date = datetime.datetime.strptime(str(end_date), '%Y-%m-%d').date()
	else:
		end_date = start_date

	all_dates = generate_date_range(start_date, end_date)
	print '\nINFO: Downloading FMS fixies from', all_dates[0], 'to', all_dates[-1], "!\n"

	good_dates = remove_weekends_and_holidays(all_dates)
	fnames = [''.join([datetime.datetime.strftime(date, '%y%m%d'), '00.txt']) for date in good_dates]
	request_all_fixies(fnames)
	return fnames

################################################################################
if __name__ == '__main__':
	try:
		start_date = datetime.datetime.strptime(str(sys.argv[1]), '%Y-%m-%d').date()
	except IndexError:
		print 'ERROR: must provide date as argument!'
		sys.exit()
	try:
		end_date = datetime.datetime.strptime(str(sys.argv[2]), '%Y-%m-%d').date()
	except IndexError:
		end_date = start_date

	download_fixies(start_date, end_date)


