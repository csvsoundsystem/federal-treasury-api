import tweepy
import re, sys, yaml
from datetime import datetime
from json import load
from urllib import urlopen
from urllib import urlencode
from pandas import DataFrame

def treasury(sql):
    url = 'https://box.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql/'
    query_string = urlencode({'q':sql})
    handle = urlopen(url + '?' + query_string)
    if handle.code == 200:
        d = load(handle)
        return DataFrame(d)
    else:
        raise ValueError(handle.read())

def connect_to_twitter(config="api.yml"):
    conf = yaml.safe_load(open(config))

    auth = tweepy.OAuthHandler(conf['consumer_key'], conf['consumer_secret'])
    auth.set_access_token(conf['access_token'], conf['access_token_secret'])
    api = tweepy.API(auth)
    return api


if __name__ == '__main__':
    print('Operating cash balances for May 22, 2013')
    print(treasury('''SELECT * FROM "t1" WHERE "date" = '2013-05-22';'''))
