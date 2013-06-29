#!/usr/bin/env python
import os, datetime
import re
import StringIO

import nose.tools as n
import pandas

from parse_fms_fixies import parse_file, strip_table_name

def check_parse(fixie_basename, i):
    observed_dict = parse_file(os.path.join('fixtures', fixie_basename + '.txt'), 'r')[i - 1]
    observed_csv  =  StringIO.StringIO()
    observed_dict.to_csv(observed_csv, index=False, header=True, encoding='utf-8', na_rep='')

    observed = observed_csv.getvalue()
    expected = open(os.path.join('fixtures', '%s_t%d.csv' % (fixie_basename, i ))).read()

    for o,e in zip(observed.split('\n'), expected.split('\n')):
        n.assert_equal(len(o), len(e))

def test_strip_clean_table_name():
    observed = strip_table_name(u'TABLE I Operating Cash Balance')
    assert observed == u'TABLE I Operating Cash Balance'

def test_strip_dirty_table_name():
    observed = strip_table_name(u'TABLE I Operating Cash Balance \xb3')
    assert observed == u'TABLE I Operating Cash Balance'


def test_daily_csv():
    for csv in filter(lambda f: '.csv' in f, os.listdir('fixtures')):
        basename, _, table, _= re.split(r'[_.t]', csv)
        yield check_parse, basename, int(table)
