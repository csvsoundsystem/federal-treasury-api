#!/usr/bin/env python

from json import load
from urllib import urlopen
from urllib import urlencode

from pandas import DataFrame

def treasury(sql):
    url = 'https://premium.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql/'
    query_string = urlencode({'q':sql})
    handle = urlopen(url + '?' + query_string)
    if handle.code == 200:
        d = load(handle)
        return DataFrame(d)
    else:
        raise ValueError(handle.read())

if __name__ == '__main__':
    print('Operating cash balances for May 22, 2013')
    print(treasury('''SELECT * FROM "t1" WHERE "date" = '2013-05-22';'''))
