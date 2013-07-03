#!/usr/bin/env python
import humanize
import math
import datetime
from optparse import OptionParser
import os, re, yaml, json
import tweepy
from random import choice
from json import load
from urllib2 import urlopen
from urllib import urlencode
from pandas import DataFrame
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
    n = humanize.intword(int(math.ceil(num))).lower()
    if re.search(r"^(\d+)\.0 ([A-Za-z]+)$", n):
        m = re.search(r"^(\d+)\.0 ([A-Za-z]+)$", n)
        n = m.group(1) + " " + m.group(2)
    return n

def style_day(n):
    n = int(n)
    return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))

def human_date(date):
    h = humanize.naturalday(datetime.datetime.strptime(date, "%Y-%m-%d")).title()

    # remove zeros
    m0 = re.search(r"([A-Za-z]+) 0([0-9])", h)
    if m0: h = "%s %s" % ( m0.group(1), m0.group(2) )

    # style day
    m_day = re.search(r"([A-Za-z]+) (\d+)", h)
    if m_day: h = "%s %s" % ( m_day.group(1), style_day(m.group(2)) )

    # lowercase yesterday
    if h in ['Yesterday', 'Today']:
        h = h.lower()
    return h

def gen_fixie_file_url(date):
    # get the url
    BASE_URL = 'https://www.fms.treas.gov/fmsweb/viewDTSFiles'
    fname = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%y%m%d") + "00.txt"

    response = get(BASE_URL,
                   params={'dir': 'a',
                    'fname': fname}
                    )
    if response.status_code == 200:
        url = response.url

    # check in working directory instead
    else:
        response = get(BASE_URL,
                       params={'dir': 'w',
                       'fname': fname}
                       )
        url = response.url

    return url

######################################
# DATA
######################################

def query(sql):
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

def connect_to_twitter(config = os.path.expanduser("~/.twitter.yml")):
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
        api = connect_to_twitter()
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
T2_ITEM_DICT = {
    "Unemployment": "Unemployment",
    "Education Department programs": "the Education Dept.",
    "Energy Department programs": "the Energy Dept.",
    "Medicaid": "Medicaid",
    "Medicare": "Medicare",
    "Social Security Benefits ( EFT )": "social security benefits",
    "NASA programs": "NASA",
    "Housing and Urban Development programs": "housing and urban development pgrms",
    "Justice Department programs": "justice dept. programs",
    "Postal Service": "the postal service",
    "Defense Vendor Payments ( EFT )": "military contractors",
    "Federal Employees Insurance Payments": "fed. employees ins. payments",
    "Fed Highway Administration programs": "the federal hwy admin.",
    "Federal Salaries ( EFT )": "federal salaries",
    "Food Stamps": "food stamps",
    "Postal Service Money Orders and Other": "postal service money orders",
    "Interest on Treasury Securities": "interest on treasury securities",
    "Temporary Assistance for Needy Families ( HHS )": "Welfare",
    "Veterans Affairs Programs": "veterans affairs programs",
    "Air Transport Security Fees": "air transport security fees",
    "Railroad Unemployment Ins": "railroad unemployement insurance",
    "FSA Tobacco Assessments": "Tobacco Taxes",
    "Agency for International Development": "USAID",
    "Securities and Exchange Commission": "the SEC",
    "Natl Railroad Retirement Inv Trust": "the Nat'l Railroad Retirment Inv. Trust",
    "Federal Communications Commission": "the FCC",
    "SEC: Stock Exchange Fees": "stock exchange fees",
    "Environmental Protection Agency": "the EPA",
    "IRS Tax Refunds Business ( EFT )": "tax refunds for businesses",
    "IRS Tax Refunds Individual ( EFT )": "tax refunds for individuals",
    "Military Active Duty Pay ( EFT )": "military active duty pay",
    "Veterans Benefits ( EFT )": "veterans benefits",
    "State Department": "the State dept.",
    "Library of Congress": "the Lib. of Congress",
    "Federal Trade Commission": "the FTC",
    "Transportation Security Admin ( DHS )": "the TSA",
    "TARP": "TARP",
    "Interior": "Interior",
    "USDA: Forest Service": "the forest service"
}

@tweet
def random_item_tweet():

    df = query('''SELECT date, item, today, type FROM t2 WHERE date = (SELECT max(date) FROM t2)''')

    the_df = df[df.item==choice([i for i in df.item if i in set(T2_ITEM_DICT.keys())])]

    # determine change
    if len(the_df) == 1:
        if the_df['type'] == "deposit":
            change = "took in"
            preposition = "from"
        elif the_df['type'] == "withdrawal":
            change = "spent"
            preposition = "on"
        val = int(the_df['today'])
    else:
        val = sum(the_df[the_df.type == 'deposit']['today']) - sum(the_df[the_df.type == 'withdrawal']['today'])
        if val > 0:
            change = "took in"
            preposition = "from"
        else:
            change = "spent"
            preposition = "on"

    # gen values
    url = gen_fixie_file_url(df['date'][0])
    the_date = human_date(df['date'][0])
    if the_date in ["Yesterday", "Today"]:
        intro = ""
    else:
        intro = "On "
    the_val = human_number(abs(val*1e6))
    the_item = T2_ITEM_DICT[str([i for i in the_df.item][0])]

    return "%s%s, the US Gov %s %s $%s %s - %s" % (intro, the_date, change, the_val, preposition, the_item, url)

@tweet
def total_debt_tweet():
    df = query('''SELECT date, close_today
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
    url = gen_fixie_file_url(df['date'][0])
    current_date = human_date(df['date'][0])
    amt = human_number(current_amt)
    delta = human_number(delta)
    previous_date = human_date(df['date'][end])

    # generate tweet
    vals = (current_date, amt, url)
    return "Think you're in debt? As of %s, the US Gov is $%s in the hole! - %s" % vals

def dist_to_debt_ceiling_tweet():

    df = query('''SELECT a.date, a.close_today AS debt_ceiling,
                          b.close_today AS debt_subject_to_ceiling,
                          a.close_today - b.close_today as distance_from_debt_ceiling
                   FROM t3c a
                   INNER JOIN t3c b ON a.date = b.date
                   WHERE a.item = "Statutory Debt Limit" AND b.item = "Total Public Debt Subject to Limit"
                   ORDER BY a.date DESC
                   LIMIT 1
                ''')

@tweet
def change_in_balance_tweet():
    df = query('''SELECT close_today - open_today AS change, date, weekday
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
    url = gen_fixie_file_url(df['date'][0])
    the_date = human_date(df['date'][0])

    # generate tweet
    vals = (change, amt, the_date, url)
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
    elif t == 'random_item':
        random_item_tweet()

