from datetime import datetime
import pandas as pd
import os
from collections import defaultdict
import types
import re
import csv

data_path = "/Users/brian/Dropbox/code/fms_parser/"
os.chdir(data_path)
# test_paths = [
#     "11011400_t1.csv",
#     "11102100_t2.csv",
#     "11102100_t3.csv",
#     "12080100_t4.csv",
#     "11072000_t5.csv",
#     "12042700_t6.csv",
#     "12042700_t7.csv",
#     "13020700_t8.csv"
# ]
# fps = [root+f for f in test_paths]

# t1 = pd.read_csv(fps[0])
# t2 = pd.read_csv(fps[1])
# t3 = pd.read_csv(fps[2])
# t4 = pd.read_csv(fps[3])
# t5 = pd.read_csv(fps[4])
# t6 = pd.read_csv(fps[5])
# t7 = pd.read_csv(fps[6])
# t8 = pd.read_csv(fps[7])

# extract table_index
def extract_tab_index(fp):
    fp_re = re.compile(r"[0-9]+_([a-z0-9]{2,3})\.csv")
    return fp_re.search(fp).group(1)


NUM = (int, long, float, complex)
STR = (str, unicode)
NONE = (types.NoneType)
DATE = (datetime)
SIMPLE = (int, long, float, complex, str, unicode, types.NoneType)

# default date format
DATE_FORMAT = re.compile(r"[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}")

def is_str(val):
    if isinstance(val, STR):
        return True
    else:
        return False

def is_num(val):
    if isinstance(val, NUM):
        return True
    else:
        return False

def is_date(val):
    if isinstance(val, DATE):
        return True
    elif isinstance(val, STR):
        if DATE_FORMAT.search(val):
            return True
        else:
            return False
    else:
        False

def is_bool(val):
    if val in [0,1]:
        return True
    elif val in[True, False]:
        return True
    else:
        return False

def test_table_name(val):
    if re.match("TABLE.*", val):
        return True
    else:
        return False

def is_wkdy(wkdy):

    WKDYS = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Satuday",
        "Sunday"
    ]

    if pd.isnull(wkdy):
        return None
    elif wkdy.strip() in frozenset(WKDYS):
        return True
    else:
        return False

def test_text_field(text):
    if is_str(text):
        if re.match("[A-Za-z0-9_-: ]+", text):
            return True
        else:
            return False

def test_col_match(tab, expected):
    return all([True if c in frozenset(expected) else False for c in tab.keys()])

def apply_test(val, fx):
    return all([fx(v) for v in val if not pd.isnull(v)])

def count_nulls(val):
    return sum([1 for v in val if pd.isnull(v)])

def test_table_columns(tab, tab_index):

    T1_COLS = ['table', 'date', 'day', 'account', 'is_total', 'close_today', 'open_today', 'open_mo', 'open_fy', 'footnote']
    T23_COLS = ['table', 'date', 'day', 'account', 'type', 'subtype', 'item', 'is_total', 'today', 'mtd', 'fytd', 'footnote']
    T45_COLS = ['table', 'date', 'day', 'surtype', 'type', 'subtype', 'item', 'is_total', 'today', 'mtd', 'fytd', 'footnote']
    T6_COLS = ['table', 'date', 'day', 'type', 'item', 'is_total', 'close_today', 'open_today', 'open_mo', 'open_fy', 'footnote']
    T78_COLS = ['table', 'date', 'day', 'type', 'classification', 'is_total', 'today', 'mtd', 'fytd', 'footnote']

    # text indiviable tables for proper columns
    if tab_index=="t1":
        return test_col_match(tab, T1_COLS)
    elif tab_index in ["t2", "t3"]:
        return test_col_match(tab, T23_COLS)
    elif tab_index in ["t4", "t5"]:
        return test_col_match(tab, T45_COLS)
    elif tab_index=="t6":
        return test_col_match(tab, T6_COLS)
    elif tab_index in ["t7", "t8"]:
        return test_col_match(tab, T78_COLS)
    else:
        raise ValueError("tab index must be in \"t1\":\"t8\"")

def test_table(fp):
    tab = pd.read_csv(fp)
    tab_index = extract_tab_index(fp)
    tests = []
    d = tab['date'][0]
    # test for cols:
    tests.append([d, fp, tab_index, "has_cols", test_table_columns(tab, tab_index), None, len(tab)])

    for c in tab.keys():
        if c=="table":
            if tab_index=="t3":
                tests.append([d, fp, tab_index, c, None, count_nulls(tab[c]), len(tab['table'])])
            else:
                tests.append([d, fp, tab_index, c, apply_test(tab[c], test_table_name), count_nulls(tab[c]), len(tab['table'])])
        elif c=="date":
            tests.append([d, fp, tab_index, c, apply_test(tab[c], is_date), count_nulls(tab[c]), len(tab['table'])])

        elif c=="open_today":
            tests.append([d, fp, tab_index, c, apply_test(tab[c], is_num), count_nulls(tab[c]), len(tab['table'])])

        elif c=="surtype":
            tests.append([d, fp, tab_index, c, apply_test(tab[c], is_str), count_nulls(tab[c]), len(tab['table'])])

        elif c=="account":
            tests.append([d, fp, tab_index, c, apply_test(tab[c], is_str), count_nulls(tab[c]), len(tab['table'])])

        elif c=="close_today":
            tests.append([d, fp, tab_index, c, apply_test(tab[c], is_num), count_nulls(tab[c]), len(tab['table'])])

        elif c=="classification":
            tests.append([d, fp, tab_index, c, apply_test(tab[c], is_str), count_nulls(tab[c]), len(tab['table'])])

        elif c=="item":
            tests.append([d, fp, tab_index, c, apply_test(tab[c], is_str), count_nulls(tab[c]), len(tab['table'])])

        elif c=="footnote":
            tests.append([d, fp, tab_index, c, apply_test(tab[c], is_str), count_nulls(tab[c]), len(tab['table'])])

        elif c=="open_fy":
            tests.append([d, fp, tab_index, c, apply_test(tab[c], is_num), count_nulls(tab[c]), len(tab['table'])])

        elif c=="open_mo":
            tests.append([d, fp, tab_index, c, apply_test(tab[c], is_num), count_nulls(tab[c]), len(tab['table'])])

        elif c=="subtype":
            tests.append([d, fp, tab_index, c, apply_test(tab[c], is_str), count_nulls(tab[c]), len(tab['table'])])

        elif c=="mtd":
            tests.append([d, fp, tab_index, c, apply_test(tab[c], is_num), count_nulls(tab[c]), len(tab['table'])])

        elif c=="mtd":
            tests.append([d, fp, tab_index, c, apply_test(tab[c], is_bool), count_nulls(tab[c]), len(tab['table'])])

        elif c=="day":
            tests.append([d, fp, tab_index, c, apply_test(tab[c], is_wkdy), count_nulls(tab[c]), len(tab['table'])])

        elif c=="type":
            tests.append([d, fp, tab_index, c, apply_test(tab[c], is_str), count_nulls(tab[c]), len(tab['table'])])

        elif c=="today":
            tests.append([d, fp, tab_index, c, apply_test(tab[c], is_num), count_nulls(tab[c]), len(tab['table'])])

        elif c=="fytd":
             tests.append([d, fp, tab_index, c, apply_test(tab[c], is_num), count_nulls(tab[c]), len(tab['table']) ])

    return tests

# test ALL the data
filepaths = ["fms_parser_data/daily_csv/" + f for f in os.listdir("fms_parser_data/daily_csv/")]
o = []
for i, fp in enumerate(filepaths):
    print str(i), "of", str(len(filepaths))
    try:
        o.extend(test_table(fp))
    except:
        pass


# output to csv.
with open("test_output/test-2013-05-13.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(o)











