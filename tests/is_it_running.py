#!/usr/bin/env python
# Tested by Tom on Python 2.7.5 and Python 3.3.1 running on Arch Linux
import json
import datetime
from requests import get
from optparse import OptionParser
from postmark import email


# gmail helper

def query(sql):
    url = 'https://premium.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql'
    r = get(url, params = {'q': sql})
    return r.json()

# is it running?
def date_pair(date_date):
    return {
        'days': (datetime.date.today() - date_date).days,
        'date': date_date.strftime('%A, %B %d, %Y'),
    }

def observed_data():
    sql = '''SELECT MAX(date) FROM t1;'''
    date_string = query(sql)[0]['MAX(date)']
    date_date = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

    return date_pair(date_date)

def expected_data():
    'The date when the script should have last run'
    adate = datetime.date.today()
    adate -= datetime.timedelta(days=1)
    while adate.weekday() >= 4: # Mon-Fri are 0-4
        adate -= datetime.timedelta(days=1)
    return date_pair(adate)

@email
def is_it_running():
    observed = observed_data()
    expected = expected_data()
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = "[treasury.io tests] is_it_running.py | %s" % today

    if (expected['days']  - observed['days']) > 3:
        msg =   """
                <p> Hello, </p>
                <p> The parser last ran on <em>%s.</em> Something is up!</p> 
                <p> xoxo, </p>
                <p> \t treasury.io</p>
                """ % expected['date']

        print "\nEMAIL: %s" % msg
        return "ERROR: " + subject, msg
        
    else:
        msg =   """
                <p> Hello, </p>
                <p> All seems well at <em>%s</em></p> 
                <p> xoxo, </p>
                <p> \t treasury.io</p>
                """ % today

        print "\nEMAIL: %s" % msg
        return subject, msg

if __name__ == '__main__':
    print "\nINFO: Testing whether the server is running as it should\n"
    try:
        is_it_running()
    except TypeError:
        pass
