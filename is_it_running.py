#!/usr/bin/env python
# Tested by Tom on Python 2.7.5 and Python 3.3.1 running on Arch Linux
'Run this script to see whether the script on ScraperWiki is running daily.'

import json
import datetime
from requests import get

def date_pair(date_date):
    return {
        'days': (datetime.date.today() - date_date).days,
        'date': date_date.strftime('%A, %B %d, %Y'),
    }

def observed():
    url = 'https://box.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql'
    sql = '''SELECT max(date) FROM t1;'''

    r = get(url, params = {'q': sql})
    date_string = json.loads(r.text)[0]['max(date)']
    date_date = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

    return date_pair(date_date)

def expected():
    'The date when the script should have last run'
    adate = datetime.date.today()
    adate -= datetime.timedelta(days=1)
    while adate.weekday() >= 4: # Mon-Fri are 0-4
        adate -= datetime.timedelta(days=1)
    return date_pair(adate)

# Error if it hasn't run in half a week.
observed = observed()
expected = expected()

print('The parser last ran on ScraperWiki %(days)d days ago, on %(date)s.' % observed)
if observed['days'] > 7:
    print("That was a week ago; something is probably wrong.")
    exit(1)
elif observed['date'] < expected['date']:
    print("It should have run on %(date)s; if that's not a holiday, something is wrong." % expected)
    exit(2)
else:
    print('All seems well.')
