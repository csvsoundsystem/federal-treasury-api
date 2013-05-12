from datetime import datetime, date
import pandas as pd
import os

test_paths = [
    "11011400_t1.csv",
    "11102100_t2.csv",
    "11102100_t3.csv",
    "12080100_t4.csv",
    "11072000_t5.csv",
    "12042700_t6.csv",
    "12042700_t7.csv",
    "13020700_t8.csv"
]
root = "fms_parser_data/daily_csv/"
fps = [root+f for f in test_paths]

t1 = pd.read_csv(fps[0])
t2 = pd.read_csv(fps[1])
t3 = pd.read_csv(fps[2])
t4 = pd.read_csv(fps[3])
t5 = pd.read_csv(fps[4])
t6 = pd.read_csv(fps[5])
t7 = pd.read_csv(fps[6])


NUM = (int, long, float, complex)
STR = (str, unicode)
NONE = (types.NoneType)
DATE = (datetime.date, datetime.datetime)
SIMPLE = (int, long, float, complex, str, unicode, types.NoneType)

def is_none(val):
    if isinstance(val, NONE) or val=="":
        return True
    else:
        False

def is_str(val):
    if is_none(val):
        return None
    elif isinstance(val, STR):
        return True
    else:
        return False

def is_num(val):
    if is_none(val):
        return None
    elif isinstance(val, NUM):
        return True
    else:
        return False

def is_date(val):
    if is_none(val):
        return None
    if isinstance(val, DATE):
        return True
    elif re.match("[0-9]{4}-[0-9]{1,2}-[0-9{1,2}")==val.strftime("%Y-%m-%d"):
        return True
    else:
        False

def is_bool(val):
    if is_none(val):
        return None
    elif val in [0,1]:
        return True
    elif val in[True, False]:
        return True
    else:
        return False

def test_table_name(table_name):
    if is_none(table_name):
        return None
    if re.match("TABLE.*", table_name):
        return True
    else:
        return False

def test_wkdy(wkdy):

    WXDYS = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Satuday",
        "Sunday"
    ]

    if is_none(wkdy):
        return None
    elif wkdy.strip() in WKDYS:
        return True
    else:
        return False

def test_text_field(text):
    if is_str(text):
        if re.match("[A-Za-z0-9_-]+", text):


def test_col_match(tab, expected):
    return [TRUE if c in frozenset(expected) else False for c in tab.columns()]


def test_table_columns(tab, tab_index, expected_cols):

    T1_COLS = ['table', 'date', 'day', 'account', 'is_total', 'close_today', 'open_today', 'open_mo', 'open_fy', 'footnote']
    T2_COLS = T3_COLS = ['table', 'date', 'day', 'account', 'type', 'subtype', 'item', 'is_total', 'today', 'mtd', 'fytd', 'footnote']
    T4_COLS = T5_COLS =  ['table', 'date', 'day', 'surtype', 'type', 'subtype', 'item', 'is_total', 'today', 'mtd', 'fytd', 'footnote']
    T6_COLS = ['table', 'date', 'day', 'type', 'item', 'is_total', 'close_today', 'open_today', 'open_mo', 'open_fy', 'footnote']
    T7_COLS = T8_COLS = ['table', 'date', 'day', 'type', 'classification', 'is_total', 'today', 'mtd', 'fytd', 'footnote']

    # text indiviable tables for proper columns
    if tab_index=="t1":
        return test_col_match(tab, T1_COLS)
    elif tab_index in ["t2", "t3"]:
        return test_col_match(tab, T2_COLS)
    elif tab_index in ["t4", "t5"]:
        return test_col_match(tab, T5_COLS)
    elif tab_index=="t6":
        return test_col_match(tab, T6_COLS)
    elif tab_index in ["t7", "t8"]:
        return test_col_match(tab, T7_COLS)
    else:
        raise ValueError("tab index must be in \"t1\":\"t8\"")



    for c in expected_cols:
        if c=="table":
            tests.append(not all([test_table_name(v) for v in value]))
        elif c=="date":
            i t.
            tests.append(is_date(t['table']))

# split up
bri_cols = [
    'open_today',
    'surtype',
    'account',
    'close_today',
    'classification',
    'item',
    'footnote',
    'open_fy',
    'open_mo',
]
bur_cols = [
    'subtype',
    'mtd',
    'is_total',
    'date',
    'table',
    'type',
    'day',
    'today',
    'fytd'


# all fields





