#!/usr/bin/env python
import treasuryio
import humanize
import math

MIL = 1e6

# Helpers to humanize numbers / dates
def human_number(num):
    return humanize.intword(int(math.ceil(num))).lower()

def human_date(date):
    return humanize.naturalday(date).title()

@treasuryio.tweet
def total_debt_tweet():
    df = treasuryio.query('SELECT date, close_today FROM t3c WHERE (item LIKE \'%subject to limit%\' AND year = 2013 AND month >=1) ORDER BY date DESC')

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
    # Notice the included ``human_date`` and ``human_number`` functions which simplify these values for you
    current_date = human_date(df['date'][0])
    amt = human_number(current_amt)
    delta = human_number(delta)
    previous_date = human_date(df['date'][end])

    # generate tweet
    vals = (current_date, amt, change, previous_date, 'http://treasury.io')
    return "As of %s, the US Gov is $%s in debt. This amount has %s since %s - %s" % vals

if __name__ == '__main__':
    total_debt_tweet()
