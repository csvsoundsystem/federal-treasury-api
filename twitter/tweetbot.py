#!/usr/bin/env python
import humanize
import math
import datetime
from optparse import OptionParser
import os
import yaml
import tweepy
from json import load
from urllib2 import urlopen
from urllib import urlencode
from pandas import DataFrame
import json
from requests import get

######################################
# HELPERS
######################################

def load_options():
    parser = OptionParser()
    parser.add_option("-t", "--tweet-type", dest="tweet_type", default="total_debt",
                  help="write report to FILE", metavar="FILE")
    (options, args) = parser.parse_args()
    return options

# Helpers to humanize numbers / dates
def human_number(num):
    return humanize.intword(int(math.ceil(num))).lower()

def human_date(date):
    h = humanize.naturalday(datetime.datetime.strptime(date, "%Y-%m-%d")).title()
    if h in ['Yesterday', 'Today']:
        h = h.lower()
    return h

######################################
# DATA
######################################

def _query(sql):
    '''
    Submit an `sql` query (string) to treasury.io and return a pandas DataFrame.

    For example::

        print('Operating cash balances for May 22, 2013')
        print(treasury.io('SELECT * FROM "t1" WHERE "date" = \'2013-05-22\';'))
    '''
    url = 'https://premium.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql/'
    query_string = urlencode({'q':sql})
    handle = urlopen(url + '?' + query_string)
    if handle.code == 200:
        d = load(handle)
        return DataFrame(d)
    else:
        raise ValueError(handle.read())


######################################
# TWITTER
######################################

def _connect_to_twitter(config = os.path.expanduser("~/.twitter.yml")):
    conf = yaml.safe_load(open(config))
    auth = tweepy.OAuthHandler(conf['consumer_key'], conf['consumer_secret'])
    auth.set_access_token(conf['access_token'], conf['access_token_secret'])
    api = tweepy.API(auth)
    return api

def tweet(tweet_text_func):
    '''
    A decorator to make a function Tweet

    Parameters

    - `tweet_text_func` is a function that takes no parameters and returns a tweetable string

    For example::

        @tweet
        def total_deposits_this_week():
            # ...

        @tweet
        def not_an_interesting_tweet():
            return 'This tweet is not data-driven.'
    '''
    def tweet_func():
        api = _connect_to_twitter()
        tweet = tweet_text_func()
        print "Tweeting: %s" % tweet
        try:
            api.update_status(tweet)
        except tweepy.error.TweepError as e:
             pass
        else:
            return tweet

    return tweet_func

######################################
# TWEETS
######################################

@tweet
def new_data_tweet():
    return ""

@tweet
def total_debt_tweet():
    df = _query('''SELECT date, close_today
                  FROM t3c
                  WHERE (item LIKE \'%subject to limit%\' AND year = 2013 AND month >=1)
                  ORDER BY date DESC''')

    # determine length of DataFrame
    end = len(df)-1

    # extract current amount and amount at the beginning of the year
    current_amt = df['close_today'][0]*1e6
    previous_amt = df['close_today'][end]*1e6

    # calculate change
    delta = abs(current_amt - previous_amt)

    # generate word to represnet the direction of change
    if current_amt > previous_amt:
        change = "increased"
    elif current_amt < previous_amt:
        change = "decreased"

    # humanize values
    # Notice the included ``human_date`` and ``human_number`` functions which simplify these values for you
    current_date = human_date(df['date'][0])
    amt = human_number(current_amt)
    delta = human_number(delta)
    previous_date = human_date(df['date'][end])

    # generate tweet
    vals = (current_date, amt, change, delta, previous_date, 'http://treasury.io')
    return "As of %s, the US Gov is $%s in debt. This amount has %s by %s since %s - %s" % vals

@tweet
def change_in_balance_tweet():
    df = _query('''SELECT close_today - open_today AS change, date, weekday
                  FROM t1
                  WHERE account = 'Total Operating Balance'
                  ORDER BY date DESC
                  LIMIT 1''')

    # calculate change
    raw_amt = df['change'][0]
    if raw_amt < 0:
        change = "dropped"
    elif raw_amt > 0:
        change = "rose"

    # humanize number and date
    amt = human_number(abs(raw_amt)*1e6)
    the_date = human_date(df['date'][0])

    # generate tweet
    vals = (change, amt, the_date, 'http://treasury.io')
    return "The US Gov's total operating balance %s $%s on %s - %s" % vals

@tweet
def is_it_running_tweet():

    def date_pair(date_date):
        return {
            'days': (datetime.date.today() - date_date).days,
            'date': date_date.strftime('%A, %B %d, %Y'),
        }

    def observed_data():
        url = 'https://premium.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql'
        sql = '''SELECT MAX(date) AS max_date FROM t1;'''

        r = get(url, params = {'q': sql})
        date_string = json.loads(r.text)[0]['max_date']
        date_date = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

        return date_pair(date_date)

    def expected_data():
        'The date when the script should have last run'
        adate = datetime.date.today()
        adate -= datetime.timedelta(days=1)
        while adate.weekday() >= 4: # Mon-Fri are 0-4
            adate -=  datetime.timedelta(days=1)
        return date_pair(adate)

    def gen_test_tweet():
        peeps = "@brianabelson @mhkeller @jbialer @thomaslevine @bdewilde @Cezary"
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

        observed = observed_data()
        expected = expected_data()

        if observed['days'] > 7:
            return "Yo %s! Something is definitely wrong! - %s" % (peeps, current_date)
        elif observed['date'] < expected['date']:
            return "Hey %s, somethings wrong unless %s is a holiday! - %s" % (peeps, expected['date'])
        else:
            return None

    return gen_test_tweet()

######################################
# SELECTOR
######################################

if __name__ == '__main__':

    options = load_options()
    t = options.tweet_type

    if t == 'total_debt':
        total_debt_tweet()
    elif t == 'change_in_balance':
        change_in_balance_tweet()
    elif t == 'is_it_running':
        is_it_running_tweet()

