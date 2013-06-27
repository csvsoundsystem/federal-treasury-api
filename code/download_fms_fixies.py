
import codecs
import datetime
import os
import pandas as pd
import requests
import sys

BASE_URL = 'https://www.fms.treas.gov/fmsweb/viewDTSFiles'
SAVE_DIR = os.path.join('..', 'data', 'fixie')

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
def remove_weekend_dates(all_dates):
	good_dates = [date for date in all_dates
				  if datetime.datetime.strftime(date, '%A') not in ['Saturday', 'Sunday']]
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
				f = codecs.open(os.path.join(SAVE_DIR, alt_fname), 'wb', 'utf-8')
				f.write(fixie)
				f.close()
				print 'INFO: saving', os.path.join(SAVE_DIR, alt_fname)
				break
		if fixie is None:
			print 'WARNING:', fname, '(',
			print str(datetime.datetime.strptime(fname[:6], '%y%m%d').date()),
			print ')', 'not available!'

################################################################################
def download_fixies(start_date, end_date=None):
	start_date = datetime.datetime.strptime(str(start_date), '%Y-%m-%d').date()
	if end_date:
		end_date = datetime.datetime.strptime(str(end_date), '%Y-%m-%d').date()
	else:
		end_date = start_date

	all_dates = generate_date_range(start_date, end_date)
	print '\nINFO: Downloading FMS fixies from', all_dates[0], 'to', all_dates[-1], "!\n"

	good_dates = remove_weekend_dates(all_dates)
	fnames = [''.join([datetime.datetime.strftime(date, '%y%m%d'), '00.txt'])
			for date in good_dates]
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


