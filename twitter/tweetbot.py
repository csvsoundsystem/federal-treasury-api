import tweepy
import humanize
import math
import re, sys, yaml
from datetime import datetime
from json import load
from urllib import urlopen
from urllib import urlencode
from pandas import DataFrame
from optparse import OptionParser

# Global vars, this way we wont need to rewrite things for every tweet.
URL = "http://treasury.io"
MIL = 1e6

# Insert new queries here.
# Each query is a key/value pair with the key being the name of the query, and the value being the query itself
QUERIES = {
    'total_debt': 'SELECT date, close_today FROM t3c WHERE (item LIKE \'%subject to limit%\' AND year = 2013 AND month >=1) ORDER BY date DESC',
    'change_in_balance': 'SELECT date, close_today - open_today AS change, weekday  FROM t1 WHERE account=\'Total Operating Balance\' ORDER BY date DESC LIMIT 1'
}
# each query key can be accessed via the command line with the -t flag
def load_options():
    parser = OptionParser()
    parser.add_option("-t", "--tweet-type", dest="tweet_type", default="total_debt",
                  help="write report to FILE", metavar="FILE")

    (options, args) = parser.parse_args()
    return options

def connect_to_twitter(config="api.yml"):
    conf = yaml.safe_load(open(config))
    auth = tweepy.OAuthHandler(conf['consumer_key'], conf['consumer_secret'])
    auth.set_access_token(conf['access_token'], conf['access_token_secret'])
    api = tweepy.API(auth)
    return api

def treasury_io(sql):
    url = 'https://premium.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql/'
    query_string = urlencode({'q':sql})
    handle = urlopen(url + '?' + query_string)
    if handle.code == 200:
        d = load(handle)
        return DataFrame(d)
    else:
        raise ValueError(handle.read())

# Helpers to humanize numbers / dates
def human_number(num):
    return humanize.intword(int(math.ceil(num))).lower()

def human_date(date):
    d = humanize.naturalday(datetime.strptime(date, "%Y-%m-%d")).title()
    if d in ["Yesterday", "Today"]:
        d = d.lower()
    return d

######################################
def total_debt_tweet(df):
    # determine length of DataFrame
    end = len(df)-1

    # extract current amount and amount at the beginning of the year
    current_amt = df['close_today'][0]*MIL
    previous_amt = df['close_today'][end]*MIL

    # calculate change
    delta = abs(current_amt - previous_amt)

    # generate word to represnet the direction of change
    if current_amt > previous_amt:
        change = "increased"
    elif current_amt < previous_amt:
        change = "decreased"

    # humanize values
    current_date = human_date(df['date'][0])
    amt = human_number(current_amt)
    delta = human_number(delta)
    previous_date = human_date(df['date'][end])

    # generate tweet
    vals = (current_date, amt, change, previous_date, URL)
    return "As of %s, the US Gov is $%s in debt. This amount has %s since %s - %s" % vals

def change_in_balance_tweet(df):

    # calculate change
    raw_amt = df['change'][0]
    if raw_amt < 0:
        change = "dropped"
    elif raw_amt > 0:
        change = "increased"
    # humanize number
    amt = human_number(abs(raw_amt)*MIL)

    #Extract Weekday
    weekday = df['weekday'][0]

    return "The US Gov's total operating balance %s by $%s on %s - %s" % (change, amt, weekday, URL)

######################################

# this is the heart of the tweet bot
# give a tweet type, it will query the database
# and pass the resulting data to a tweet constructor
def construct_tweet(options):
    t = options.tweet_type
    df = treasury_io(QUERIES[t])
    if t == 'total_debt':
        return total_debt_tweet(df)
    elif t == 'change_in_balance':
        return change_in_balance_tweet(df)

if __name__ == '__main__':
    options = load_options()
    api = connect_to_twitter()
    tweet = construct_tweet(options)
    print "TWEET:", tweet
    api.update_status(tweet)

