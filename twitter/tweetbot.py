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

# Insert new queries here.
# Each query is a key/value pair with the key being the name of the query, and the value being the query itself
QUERIES = {
    'total_debt': '''SELECT date, close_today FROM t3c WHERE item LIKE \'%subject to limit%\' ORDER BY date DESC LIMIT 30'''
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

def query_treasury(sql):
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
    return humanize.naturalday(date).title()


# this is the heart of the tweet bot
# give a tweet type, it will query the database
# for each tweet type, we will then calculate something and
def construct_tweet(options):
    t = options.tweet_type

    # total debt
    if t == 'total_debt':
        q = QUERIES[t]
        df = query_treasury(q)
        num = human_number(df['close_today'][0]*1e6)
        date = human_date(datetime.strptime(df['date'][0], "%Y-%m-%d"))
        tweet = "As of %s, the US Government is $%s in debt. Learn more at %s" % (date, num, URL)

    return tweet

if __name__ == '__main__':
    options = load_options()
    api = connect_to_twitter()
    tweet = construct_tweet(options)
    print "TWEET:", tweet
    api.update_status(tweet)

