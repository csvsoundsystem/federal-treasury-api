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

def observed_data():
    url = 'https://premium.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql'
    sql = '''SELECT max(date) FROM t1;'''

    r = get(url, params = {'q': sql})
    date_string = json.loads(r.text)[0]['max(date)']
    date_date = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

    return date_pair(date_date)

def expected_data():
    'The date when the script should have last run'
    adate = datetime.date.today()
    adate -= datetime.timedelta(days=1)
    while adate.weekday() >= 4: # Mon-Fri are 0-4
        adate -= datetime.timedelta(days=1)
    return date_pair(adate)

# Error if it hasn't run in half a week.
def gen_message(tweet=True):
    peeps = "@brianabelson @mhkeller @jbialer @thomaslevine @bdewilde @Cezary"
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    observed = observed_data()
    expected = expected_data()

    if observed['days'] > 7:
        if tweet:
            return "Yo %s! Something is definitely wrong! - %s" % (peeps, current_date)
        else:
            return "The parser last ran on %s. Something is definitely wrong!" % observed['date']

    elif observed['date'] < expected['date']:
        if tweet:
            return "Hey %s, somethings wrong if %s is a holiday! - %s" % (peeps, expected['date'])
        else:
            return "Unless %s is a holiday, something is up!" % expected['date']
    else:
        if tweet:
            return None
        else:
            return "All seems well!"

if __name__ == '__main__':
    print gen_message(tweet=False)