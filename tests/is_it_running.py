#!/usr/bin/env python
# Tested by Tom on Python 2.7.5 and Python 3.3.1 running on Arch Linux
import json
import datetime
from requests import get
from optparse import OptionParser

def load_options():
    parser = OptionParser()
    parser.add_option("-t", "--tweet", dest="tweet", default=False,
                  help="Whether or not to tweet results for test")
    (options, args) = parser.parse_args()
    return options

def date_pair(date_date):
    return {
        'days': (datetime.date.today() - date_date).days,
        'date': date_date.strftime('%A, %B %d, %Y'),
    }

def observed_data():
    url = 'https://premium.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql'
    sql = '''SELECT MAX(date) FROM t1;'''

    r = get(url, params = {'q': sql})
    date_string = json.loads(r.text)[0]['MAX(date)']
    date_date = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

    return date_pair(date_date)

def expected_data():
    'The date when the script should have last run'
    adate = datetime.date.today()
    adate -= datetime.timedelta(days=1)
    while adate.weekday() >= 4: # Mon-Fri are 0-4
        adate -= datetime.timedelta(days=1)
    return date_pair(adate)

def gen_test_message():
    observed = observed_data()
    expected = expected_data()

    if observed['days'] > y:
        print "The parser last ran on %s. Something is definitely wrong!" % observed['date']
    elif observed['date'] < expected['date']:
        print "Unless %s is a holiday, something is up!" % expected['date']
    else:
        print "All seems well!"

if __name__ == '__main__':
    gen_test_message()
