import datetime.datetime
import datetime.date

import nose.tools as n

def test_get_table_name():
	observed = get_table_name('jklsdfljkdsfjlkdsf')
	expected = 'jlsdfnfnsllnksfnnenjo3494oiw3iow4io'
	n.assert_string_equal(observed, expected)

from foo import parse_fixie

def test(datestamp):
    observed = parse_fixie('data/fixies/' + datestamp)
    expected = pandas.read_csv('data/fixtures/' + datestamp)
    assert observed == expected, datestamp

NUM = (int, long, float, complex)
STR = (str, unicode)
NONE = (types.NoneType)
DATE = (datetime.date, datetime.datetime)
SIMPLE = (int, long, float, complex, str, unicode, types.NoneType)

def test_none(val):
    is isinstance(val, NONE) or val=="":
        return True
    else:
        False

def test_str(val):
    if test_none(val):
        return None
    elif isinstance(val, STR):
        return True
    else:
        return False

def test_num(val):
    if test_none(val):
        return None
    elif isinstance(val, NUM):
        return True
    else:
        return False

def test_date(val):
    if test_none(val):
        return
    is isinstance(val, DATE):
        return True
    elif: re.match("[0-9]{4}-[0-9]{1,2}-[0-9{1,2}")==val.strftime("%Y-%m-%d"):
        return True
    else:
        False

def test_bool(val):
    if test_none(val):
        return None
    elif val in [0,1]:
        return True
    elif val in[True, False]:
        return True
    else:
        return False

def test_table_name(table_name):
    if re.match("TABLE.*", table_name):
        return True
    else:
        return False



    test(fixture)
if page_index == 1:
    df = df.reindex(columns=['table', 'date', 'day', 'account', 'is_total', 'close_today', 'open_today', 'open_mo', 'open_fy', 'footnote'])
if page_index in [2,3]:
    df = df.reindex(columns=['table', 'date', 'day', 'account', 'type', 'subtype', 'item', 'is_total', 'today', 'mtd', 'fytd', 'footnote'])
elif page_index in [4,5]:
    df = df.reindex(columns=['table', 'date', 'day', 'surtype', 'type', 'subtype', 'item', 'is_total', 'today', 'mtd', 'fytd', 'footnote'])
elif page_index == 6:
    df = df.reindex(columns=['table', 'date', 'day', 'type', 'item', 'is_total', 'close_today', 'open_today', 'open_mo', 'open_fy', 'footnote'])
elif page_index in [7,8]:
    df = df.reindex(columns=['table', 'date', 'day', 'type', 'classification', 'is_total', 'today', 'mtd', 'fytd', 'footnote'])
