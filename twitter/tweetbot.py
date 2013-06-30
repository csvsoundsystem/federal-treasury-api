#!/usr/bin/env python
import treasuryio
import humanize
import math
from datetime import datetime
from optparse import OptionParser

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
    return humanize.naturalday(datetime.strptime(date, "%Y-%m-%d")).title()

######################################
@treasuryio.tweet
def new_data_tweet():
    return ""

@treasuryio.tweet
def total_debt_tweet():
    df = treasuryio.query('''SELECT date, close_today
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

######################################
@treasuryio.tweet
def change_in_balance_tweet():
    df = treasuryio.query('''SELECT close_today - open_today AS change, date, weekday
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

######################################

if __name__ == '__main__':

    options = load_options()
    t = options.tweet_type

    if t == 'total_debt':
        total_debt_tweet()
    elif t == 'change_in_balance':
        change_in_balance_tweet()

