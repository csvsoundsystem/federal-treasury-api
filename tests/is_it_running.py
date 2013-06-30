#!/usr/bin/env python
# Tested by Tom on Python 2.7.5 and Python 3.3.1 running on Arch Linux

import json
import datetime
from requests import get


def date_pair(date_date):
    return {
        'days': (datetime.date.today() - date_date).days,
        'date': date_date.strftime('%A, %B %d, %Y'),
    }

def observed():
    url = 'https://premium.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql'
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
def produce_message():
    PEEPS = "@brianabelson @mhkeller @jbialer @thomaslevine @bdewilde @Cezary"
    observed = observed()
    expected = expected()
    if observed['days'] > 7:
        return twt =  "%s - something is definitely wrong at %s" % (PEEPS, datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S"))

    elif observed['date'] < expected['date']:
        print("If %(date)s;  that's not a holiday, something is wrong." % expected)
        exit(2)
    else:
        print('All seems well.')
