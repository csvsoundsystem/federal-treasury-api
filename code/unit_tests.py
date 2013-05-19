from datetime import datetime
import pandas as pd
import os
from collections import defaultdict
import types
import re
import csv

NUM = (int, long, float, complex)
STR = (str, unicode)
NONE = (types.NoneType)
DATE = (datetime)
SIMPLE = (int, long, float, complex, str, unicode, types.NoneType)

# default date format
DATE_FORMAT = re.compile(r"[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}")

def is_str(val):
    if pd.isnull(val):
        return "missing"
    if isinstance(val, STR):
        return "passed"
    else:
        return "failed"

def is_num(val):
    if pd.isnull(val):
        return "missing"
    elif isinstance(val, NUM):
        return "passed"
    else:
        return "failed"

def is_date(val):
    if pd.isnull(val):
        return "missing"
    elif isinstance(val, DATE):
        return "passed"
    elif isinstance(val, STR):
        if DATE_FORMAT.search(val):
            return "passed"
        else:
            return "failed"
    else:
        "failed"

def is_bool(val):
    if pd.isnull(val):
        return "missing"
    elif val in [0,1]:
        return "passed"
    elif val in[True, False]:
        return "passed"
    else:
        return "failed"

def is_table(val):
    if pd.isnull(val):
        return "missing"
    if re.match("TABLE.*", val):
        return "passed"
    else:
        return "failed"

def is_wkdy(wkdy):

    WKDYS = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Satuday", "Sunday"
    ]

    if pd.isnull(wkdy):
        return "missing"
    elif wkdy.strip() in frozenset(WKDYS):
        return "passed"
    else:
        return "failed"

def test_text_field(text):
    if pd.isnull(text):
        return "missing"
    if is_str(text):
        if re.match("[A-Za-z0-9_-: ]+", text):
            return "passed"
        else:
            return "failed"

def apply_test(val, fx):

    # run tests
    tests = [fx(v) for v in val]

    # count passed, missing, failed
    n_p = n_m = n_f = 0
    for t in tests:
        if t=='passed': n_p+=1
        elif t=='missing': n_m+=1
        else: n_f+=1

    # determine if all tests passes
    if n_m + n_f==0:
        a_t = 1
    else:
        a_t = 0

    return [n_p, n_m, n_f, at]

def get_missing_cols(tab, expected):
    return [c for c in tab.keys() if c not in frozenset(expected)]

def test_table_columns(tab, ti):

    T1_COLS = ['table', 'date', 'day', 'account', 'is_total', 'close_today', 'open_today', 'open_mo', 'open_fy', 'footnote']
    T23_COLS = ['table', 'date', 'day', 'account', 'type', 'subtype', 'item', 'is_total', 'today', 'mtd', 'fytd', 'footnote']
    T45_COLS = ['table', 'date', 'day', 'surtype', 'type', 'subtype', 'item', 'is_total', 'today', 'mtd', 'fytd', 'footnote']
    T6_COLS = ['table', 'date', 'day', 'type', 'item', 'is_total', 'close_today', 'open_today', 'open_mo', 'open_fy', 'footnote']
    T78_COLS = ['table', 'date', 'day', 'type', 'classification', 'is_total', 'today', 'mtd', 'fytd', 'footnote']

    # text indiviable tables for proper columns
    if ti=="t1":
        return get_missing_cols(tab, T1_COLS)
    elif ti in ["t2", "t3"]:
        return get_missing_cols(tab, T23_COLS)
    elif ti in ["t4", "t5"]:
        return get_missing_cols(tab, T45_COLS)
    elif ti=="t6":
        return get_missing_cols(tab, T6_COLS)
    elif ti in ["t7", "t8"]:
        return get_missing_cols(tab, T78_COLS)
    else:
        raise ValueError("tab index must be in \"t1\":\"t8\"")

# extract table_index
def extract_ti(fp):
    fp_re = re.compile(r"[0-9]+_([a-z0-9]{2,3})\.csv")
    return fp_re.search(fp).group(1)

#Columns to output in testing

cols = [
    'tab_index', 'filepath', 'row_count', 'date', 'missing_cols',
    'variable', 'n_pass', 'n_miss', 'n_fail', 'all_true'
]

def test_table(fp):
    tab = pd.read_csv(fp) # read in csv
    ti = extract_tab_index(fp) # extract tab index from filepath
    l = len(tab['table']) # number of rows for this table
    d = tab['date'][0] # the date this file was released
    missing_cols = " ".join(test_table_columns(tab, ti)).strip() # a string of missing columns
    attr = [ti, fp, l, d, missing_cols] # add static fiels to "attr"

    #output shell
    tests = []
    # add column test

    for c in tab.keys():

        if c=="table":
            tests.append(attr + [c] + apply_test(tab[c], is_table))
        # unit tests ?
        elif c=="date":
            tests.append(attr + [c] + apply_test(tab[c], is_date))

        elif c=="open_today":
            tests.append(attr + [c] + apply_test(tab[c], is_num))

        elif c=="surtype":
            tests.append(attr + [c] + apply_test(tab[c], is_str))

        elif c=="account":
            tests.append(attr + [c] + apply_test(tab[c], is_str))

        elif c=="close_today":
            tests.append(attr + [c] + apply_test(tab[c], is_num))

        elif c=="classification":
            tests.append(attr + [c] + apply_test(tab[c], is_str))

        elif c=="item":
            tests.append(attr + [c] + apply_test(tab[c], is_str))

        elif c=="footnote":
            tests.append(attr + [c] + apply_test(tab[c], is_str))

        elif c=="open_fy":
            tests.append(attr + [c] + apply_test(tab[c], is_num))

        elif c=="open_mo":
            tests.append(attr + [c] + apply_test(tab[c], is_num))

        elif c=="subtype":
            tests.append(attr + [c] + apply_test(tab[c], is_str))

        elif c=="mtd":
            tests.append(attr + [c] + apply_test(tab[c], is_num))

        elif c=="day":
            tests.append(attr + [c] + apply_test(tab[c], is_wkdy))

        elif c=="type":
            tests.append(attr + [c] + apply_test(tab[c], is_str))

        elif c=="today":
            tests.append(attr + [c] + apply_test(tab[c], is_num))

        elif c=="fytd":
             tests.append(attr + [c] + apply_test(tab[c], is_num))
        else:
            raise ValueError("%s has keys that shouldn't be in the Data Set ")

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
with open("test_output/test-2013-05-14.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(cols.extend(o))











