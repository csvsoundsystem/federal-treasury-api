#!/usr/bin/env python
from __future__ import absolute_import, print_function

import argparse
import datetime
import io
import json
import logging
from operator import itemgetter
import os
import re
import sys

import arrow
import pandas as pd
import requests

from .constants import (DEFAULT_FIXIE_DIR, DEFAULT_DAILY_CSV_DIR,
                        PARSER_DIR, TABLE_KEYS)
from .utils import (get_all_dates, get_date_from_fname,
                    get_daily_csvs_by_date, get_fixies_by_date)


LOGGER = logging.getLogger('parse_fms_fixies')
LOGGER.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(name)s | %(levelname)s | %(message)s')
_handler.setFormatter(_formatter)
LOGGER.addHandler(_handler)

T4_USE_ITEMS = {
    'Tax and Loan Accounts',
    'Inter agency Transfers',
    'Federal Reserve Account Direct',
    'Federal Reserve Account Total',
    'Federal Reserve Account Depositaries',
    }

with io.open(os.path.join(PARSER_DIR, 'normalize_field_table.json'), mode='rt') as f:
    NORMALIZE_FIELD_TABLE = json.load(f)

with io.open(os.path.join(PARSER_DIR, 'errant_footnote_patterns.txt'), mode='rt') as f:
    ERRANT_FOOTNOTE_PATTERNS = tuple(
        line.strip() for line in f.readlines() if line.strip())

# TODO
# with io.open('../tests/null_test_params.json', mode='rt') as f:
#     NULL_TEST_PARAMS = json.load(f)

re_net = re.compile(".*\(.*net.*\).*", flags=re.IGNORECASE)
re_net_remove = re.compile('\(.*net.*\)', flags=re.IGNORECASE)


def is_errant_footnote(line):
    return any(re.search(p, line, flags=re.IGNORECASE)
               for p in ERRANT_FOOTNOTE_PATTERNS)


def normalize_fields(text, table, field):
    table_lookup = NORMALIZE_FIELD_TABLE[table]
    try:
        value_lookup = table_lookup[field]
    except KeyError:
        return text
    else:
        try:
            value = value_lookup[text]
        except KeyError:
            return text
        else:
            return value


def get_table_name(line):
    try:
        table_line = re.search(r'\s+TABLE\s+[\w-]+.*', line).group()
        table_name = table_line.strip()
    except AttributeError:
        table_name = None
    return table_name


def get_footnote(line):
    footnote = re.search(r'^\s*(\d)\/([\w\s\./,]+.*)', line)
    if footnote:
        return [footnote.group(1), footnote.group(2)]
    return None


def normalize_page_text(page):
    # ignore unicode errors
    # i.e. remove superscript 3 symbols ('\xc2\xb3') by way of ignoring their errors
    # hopefully this doesn't have any undesirable side-effects
    page = re.sub("\xc2\xa0|\xc2\xb3", "", page)
    # split on line breaks, usually '\r\n' and rarely just '\n'
    lines = re.split(r'\r\n|\n', page)
    # get rid of pipe delimiters and divider lines
    lines = [re.sub(r'^ \|', '       ', line) for line in lines]
    lines = [re.sub(r'\|', '', line) for line in lines]
    lines = [re.sub(r'\s?_{5,}', '', line) for line in lines]
    # get rid of dollar signs and thousand commas
    lines = [re.sub(r'\$', '', line) for line in lines]
    lines = [re.sub(r'(\d),(\d)', r'\1\2', line) for line in lines]
    # normalize non-leading white space
    lines = [line[:6] + re.sub(r'\s{2,}', ' ', line[6:]) for line in lines]
    lines = [line.rstrip() for line in lines]
    # get rid of blank lines
    lines = [line for line in lines if line != '' and line != ' ']
    return lines


def check_fixie_url(url):
    LOGGER.debug("checking %s to make sure it's valid", url)
    r = requests.head(url)
    if r.status_code == 200:
        return url
    else:
        # what directory are we in?
        bad_dir = re.search('.*dir=([aw])$', url).group(1)
        if bad_dir == 'a':
            good_dir = 'w'
        elif bad_dir == 'w':
            good_dir = 'a'
        return re.sub("dir=" + bad_dir, "dir=" + good_dir, url)


def gen_fixie_url(fname, date):
    """Super awkward function whose purpose isn't entirely clear."""
    # split the filename from the rest of its path
    _, fname = os.path.split(fname)

    # arbitrary cutoff to determine archive and working directories
    rolling_cutoff = arrow.utcnow().shift(days=-50)
    if date < rolling_cutoff.date():
        f_dir = "a"
    else:
        f_dir = "w"

    # format the url
    url = 'https://www.fms.treas.gov/fmsweb/viewDTSFiles?fname={}&dir={}'.format(fname, f_dir)

    # now lets check urls that fall within 15 days before and after our rolling cutoff
    check_cutoff_start = rolling_cutoff.shift(days=-15).date()
    check_cutoff_end = rolling_cutoff.shift(days=15).date()
    if date > check_cutoff_start and date < check_cutoff_end:
        url = check_fixie_url(url)

    return url


def check_for_nulls(df, table):
    print("TO DO")
    # test_params = NULL_TEST_PARAMS[table]
    # null_rows = []
    # for v in test_params["values"]:
    # 	null_row = df.loc(i, ) for i in df.index if pd.isnull(df[v][i])
    # 	null_rows.append(null_row)
    # null_field_values = []
    # for f in test_params['fields']
    # 	[r[f] for r in null_rows


def parse_all_fixies(filepaths, data_dir):
    """
    Args:
        filepaths (Iterable[str])
        data_dir (str)
    """
    for filepath in filepaths:
        _, fname = os.path.split(filepath)
        froot, _ = os.path.splitext(fname)

        dfs = parse_fixie(filepath)
        if dfs:
            for table_key, df in sorted(dfs.items(), key=itemgetter(0)):
                daily_csv_fname = os.path.join(
                    data_dir, froot + '_' + table_key + '.csv')
                df.to_csv(
                    daily_csv_fname,
                    index=False, header=True, encoding='utf-8', na_rep='')
                LOGGER.debug(
                    'parsed %s and saved it to %s',
                    table_key, daily_csv_fname)
        else:
            LOGGER.warning('error parsing fixie %s', fname)


def parse_fixie(fname):
    """
    Args:
        fname (str)

    Returns:
        Dict[str, :class:`pd.DataFrame`]
    """
    with io.open(fname, mode='rb') as f:
        data = f.read()

    # file metadata
    date = get_date_from_fname(fname)
    url = gen_fixie_url(fname, date)

    LOGGER.debug('parsing %s (%s)', fname, date)

    # split the file on table names
    # use regex parens to *keep* the delimiters, then clean them up
    # skip the first one, which is just the fixie header info
    re_raw_table_name = re.compile(r'([\s_]+TABLE[\s_]+[\w_-]+.*)')
    raw_tables = re_raw_table_name.split(data)
    dfs = {}
    for raw_table in raw_tables[1:]:
        try:
            if re_raw_table_name.search(raw_table):
                # fix malformed fixie table names, BLERGH GOV'T!
                table_name = re.sub(r'_+', ' ', raw_table)
                # then convert it into a standardized "key"
                table_key = re.sub(
                    r'-| ', '_',
                    re.search(r'TABLE [\w-]+', table_name).group().lower()
                    )
                if table_key not in TABLE_KEYS:
                    raise ValueError()
                continue
            raw_table = table_name + raw_table
            table = normalize_page_text(raw_table)
            dfs[table_key] = parse_table(table, date, url)
        except Exception as e:
            LOGGER.exception('error parsing fixie table %s', table_key)

    return dfs


def parse_table(table, date, url):

    # table defaults
    t4_total_count = 0
    indent = 0
    footnotes = {}
    index = surtype_index = type_index = subtype_index = used_index = -1
    type_indent = subtype_indent = -1
    page_number = -1
    type_ = subtype = None
    table_name = None

    # total hack for when the treasury decided to switch
    # which (upper or lower) line of two-line items gets the 0s
    # NOTE: THIS IS ONLY FOR TABLE I, BECAUSE OF COURSE
    if datetime.date(2012, 6, 1) <= date <= datetime.date(2013, 1, 3):
        two_line_delta = -1
    else:
        two_line_delta = 1

    parsed_table = []
    for i, line in enumerate(table):
        # print('|' + line + '|', '<', i, '>')
        row = {}

        # a variety of date formats -- for your convenience
        row['date'] = date
        row['year'] = date.year
        row['month'] = date.month
        row['day'] = date.day
        row['year_month'] = datetime.datetime.strftime(date, '%Y-%m')
        row['weekday'] = datetime.datetime.strftime(date, '%A')
        row['url'] = url

        # what's our line number? shall we bail out?
        index += 1
        if index <= used_index:
            continue
        indent = len(re.search(r'^\s*', line).group())

        # rows that we definitely want to skip
        # empty rows or centered header rows
        if re.match(r'^\s{7,}', line):
            continue

        # page number rows
        page_number_match = re.search(r'\d+.*DAILY\s+TREASURY\s+STATEMENT.*PAGE:\s+(\d+)', line)
        if page_number_match:
            page_number = page_number_match.group(1)
            continue

        # HARD CODED HACKS
        # catch rare exceptions to the above
        if re.search(r'DAILY\s+TREASURY\s+STATEMENT', line):
            continue  # ok
        # comment on statutory debt limit at end of Table III-C, and beyond
        elif (re.search(r'(As|Act) of ([A-Z]\w+ \d+, \d+|\d+\/\d+\/\d+)', line) and
                re.search(r'(statutory )*debt( limit)*', line)):
            break  # ok
        # comment on whatever this is; above line may make this redundant
        elif re.search(r'\s*Unamortized Discount represents|amortization is calculated daily',
                       line, flags=re.IGNORECASE):
            break  # ok
        # more cruft of a similar sort
        elif re.search(r'billion after \d+\/\d+\/\d+', line):
            continue  # ok
        elif re.search(r'.*r\-revised.*', line):
            continue  # ok
        elif is_errant_footnote(line):
            break  # ok

        # skip table header rows
        if get_table_name(line):
            table_name = get_table_name(line)
            continue

        row['table'] = table_name

        # save footnotes for later assignment to their rows
        footnote = get_footnote(line)

        if footnote is not None:
            # while footnote does not end in valid sentence-ending punctuation...
            i = 1
            while True:
                # get next line, if it exists
                try:
                    next_line = table[index + i]
                except IndexError:
                    break
                # and next line is not itself a new footnote...
                else:
                    if re.search('\d+.*DAILY\s+TREASURY\s+STATEMENT.*PAGE:\s+(\d+)', next_line):
                        break  # ok
                    if not get_footnote(next_line):
                        # add next line text to current footnote
                        footnote[1] = ''.join([footnote[1], next_line])
                        used_index = index + i
                        i += 1
                    if footnote[1].endswith("program."):
                        continue  # ok
                    elif re.search(r'[.!?]$', footnote[1]):
                        break  # ok

            # make our merged footnote hack official!
            footnotes[footnote[0]] = re.sub("\s{2,}", "", footnote[1])

            # if next line after footnote is not another footnote
            # it is most assuredly extra comments we don't need
            try:
                last_line = table[index + i]
            except IndexError:
                break  # ok

            else:
                if re.search('\d+.*DAILY\s+TREASURY\s+STATEMENT.*PAGE:\s+(\d+)', last_line):
                    continue  # ok
                elif re.search(r'\.aspx\.', last_line):
                    continue  # ok
                elif not get_footnote(last_line):
                    break  # ok

            # *****THIS LINE MUST BE HERE TO ENSURE THAT FOOTNOTES AREN'T INCLUDED AS ITEMS ******#
            continue

        # note rows with footnote markers for later assignment
        if re.search(r'\d+\/', line):
            row['footnote'] = re.search(r'(\d+)\/', line).group(1)

        # separate digits and words
        digits = re.findall(r'(-{,1}\d+)', line)
        words = re.findall(r'\(\-\)|[()]|[^\W\d]+:?', line)

        # check for (-) in words => multiply all digits by -1
        if '(-)' in words:
            digits = [str((-1)*int(digit)) for digit in digits]

        # bug fix, to remove the govt's usage of 'r/' in front of numbers
        # to denote revised values, and the abhorrent usage of '(-)''
        text = ' '.join(word for word in words if word not in ['r', '(-)'])

        # get type row
        if len(digits) == 0 and text.endswith(':') and indent == 1:
            type_ = text[:-1]
            type_indent = indent
            type_index = index
            continue
        elif indent <= type_indent:
            type_ = None

        row['type'] = type_

        # special handling for table 3c
        if re.search(r'TABLE III-C', row.get('table', '')):
            if re.search(r'Less: Debt Not', text):
                subtype = 'Debt Not Subject to Limit'
                subtype_indent = indent
                subtype_index = index
                continue
            elif re.search(r'Plus: Other Debt', text):
                subtype = 'Other Debt Subject to Limit'
                subtype_indent = indent
                subtype_index = index
                continue
        # get subtype row
        elif len(digits) == 0 and text.endswith(':'):
            subtype = text[:-1]
            subtype_indent = indent
            subtype_index = index
            continue

        if index == subtype_index + 1:
            pass  # possibly unnecessary
        elif indent <= subtype_indent:
            subtype = None
        row['subtype'] = subtype

        # get and merge two-line rows
        if len(digits) == 0 and not text.endswith(':'):

            if two_line_delta == 1 or not re.search(r'TABLE I\s', row.get('table', '')):

                try:
                    next_line = table[index + 1]

                    # check for footnotes, then note and erase them if present!
                    if re.search(r'\d+\/', next_line):
                        row['footnote'] = re.search(r'(\d+)\/', next_line).group(1)
                        next_line = re.sub(r'\d+\/', '', next_line)

                    next_digits = re.findall(r'(\d+)', next_line)
                    next_words = re.findall(r'[^\W\d]+:?', next_line)

                    if len(next_digits) != 0:
                        text = text + ' ' + ' '.join(next_words)
                        digits = next_digits
                        used_index = index + 1

                except IndexError:
                    pass

            elif two_line_delta == -1 and re.search(r'TABLE I\s', row.get('table', '')):

                try:
                    prev_line = table[index - 1]
                    prev_digits = re.findall(r'(\d+)', prev_line)
                    prev_words = re.findall(r'[^\W\d]+:?', prev_line)

                    if len(prev_digits) != 0:
                        text = ' '.join(prev_words) + ' ' + text
                        digits = prev_digits
                        get_rid_of_prev_line = parsed_table.pop()

                except IndexError:
                    pass

        # skip table annotations that aren't footnotes
        # this is a band-aid at best, sorry folks
        if len(digits) == 0:
            continue
        if len(text) > 80:
            continue

        row['is_total'] = int('total' in text.lower())

        # parse one table at a time...
        if re.search(r'TABLE I\s', row.get('table', '')):
            try:
                row['account_raw'] = text
                row['account'] = normalize_fields(text, 't1', 'account')
                row['close_today'] = digits[-4]
                row['open_today'] = digits[-3]
                row['open_mo'] = digits[-2]
                row['open_fy'] = digits[-1]
            except Exception:
                LOGGER.debug('table-i line exception: %s', line)

        elif re.search(r'TABLE II\s', row.get('table', '')):
            try:
                row['item_raw'] = text

                # determine whether item is calculated as a net
                if re_net.search(text):
                    row['is_net'] = 1
                else:
                    row['is_net'] = 0

                # remove net from items
                text = re_net_remove.sub("", text).strip()

                # proceed
                row['item'] = normalize_fields(text, 't2', 'item')
                row['today'] = digits[-3]
                row['mtd'] = digits[-2]
                row['fytd'] = digits[-1]
                # tweak column names
                row['account'] = row.get('type')
                # this is a hack, deal with it :-/
                row['transaction_type'] = 'deposit'
                if int(page_number) == 3:
                    row['transaction_type'] = 'withdrawal'
                # now handle items with sub-classification
                if row.get('subtype') is not None:
                    row_subtype = row['subtype']
                    row_item = row['item']
                    row['parent_item'] = row_subtype
                    row['item'] = row_item
                    row['item_raw'] = row_item_raw
                    row.pop('subtype')
            except Exception:
                LOGGER.debug('table-ii line exception: %s', line)

        elif re.search(r'TABLE III-A', row.get('table', '')):
            try:
                row['item_raw'] = text
                row['item'] = normalize_fields(text, "t3a", 'item')
                row['today'] = digits[-3]
                row['mtd'] = digits[-2]
                row['fytd'] = digits[-1]
                # tweak column names
                row['debt_type'] = row.get('type')
                # now handle items with sub-classification
                if row.get('subtype') is not None:
                    row_subtype = row['subtype']
                    row_item = row['item']
                    row['parent_item'] = row_subtype
                    row['item'] = row_item
                    row['item_raw'] = row_item_raw
                    row.pop('subtype')
            except Exception:
                LOGGER.debug('table-iiia line exception: %s', line)

        elif re.search(r'TABLE III-B', row.get('table', '')):
            try:
                row['item_raw'] = text
                row['item'] = normalize_fields(text, "t3b", 'item')
                row['today'] = digits[-3]
                row['mtd'] = digits[-2]
                row['fytd'] = digits[-1]
                # tweak column names
                row['transaction_type'] = row.get('type')
                # now handle items with sub-classification
                if row.get('subtype') is not None:
                    row_subtype = row['subtype']
                    row_item = row['item']
                    row['parent_item'] = row_subtype
                    row['item'] = row_item
                    row['item_raw'] = row_item_raw
                    row.pop('subtype')
            except Exception:
                LOGGER.debug('table-iiib line exception: %s', line)

        elif re.search(r'TABLE III-C', row.get('table', '')):
            try:
                row['item_raw'] = text
                row['item'] = normalize_fields(text, 't3c', 'item')
                row['close_today'] = digits[-4]
                row['open_today'] = digits[-3]
                row['open_mo'] = digits[-2]
                row['open_fy'] = digits[-1]
                # now handle items with sub-classification
                if row.get('subtype') is not None:
                    row['parent_item'] = row['subtype']
                    row.pop('subtype')
            except Exception:
                LOGGER.debug('table-iiic line exception: %s', line)

        elif re.search(r'TABLE IV', row.get('table', '')):
            try:
                row['type'] = ''
                row['classification_raw'] = text
                this_class = normalize_fields(text, 't4', 'classification')
                row['classification'] = this_class
                row['today'] = digits[-3]
                row['mtd'] = digits[-2]
                row['fytd'] = digits[-1]
                # increment Total counts
                if this_class == "Total":
                    t4_total_count += 1
                # assign source and use types
                if t4_total_count == 1 and this_class == "Total":
                    row['type'] = "source"
                elif t4_total_count == 2 and this_class == "Total":
                    row['type'] = "use"
                elif this_class not in T4_USE_ITEMS:
                    row['type'] = "source"
                else:
                    row['type'] = "use"
            except Exception:
                LOGGER.debug('table-iv line exception: %s', line)

        elif re.search(r'TABLE V\s', row.get('table', '')):
            try:
                row['balance_transactions'] = text
                row['depositary_type_a'] = digits[-4]
                row['depositary_type_b'] = digits[-3]
                row['depositary_type_c'] = digits[-2]
                row['total'] = digits[-1]
                # tweak column names
                row['transaction_type'] = row.get('type')
            except Exception:
                LOGGER.debug('table-v line exception: %s', line)

        elif re.search(r'TABLE VI', row.get('table', '')):
            try:
                row['refund_type_raw'] = text
                row['refund_type'] = normalize_fields(text, 't6', 'classification')
                row['today'] = digits[-3]
                row['mtd'] = digits[-2]
                row['fytd'] = digits[-1]
                if '( eft )' in row.get('refund_type_raw', '').lower():
                    row['refund_method'] = 'EFT'
                elif '( checks )' in row.get('refund_type_raw', '').lower():
                    row['refund_method'] = 'CHECKS'
            except Exception:
                LOGGER.debug('table-vi line exception: %s', line)

        parsed_table.append(row)

    # assign footnotes to rows
    # and split table III-a by surtype
    for row in parsed_table:
        if row.get('footnote'):
            row['footnote'] = footnotes.get(row['footnote'])
        if row.get('item'):
            if row['item'].lower().strip() == 'total issues':
                surtype_index = parsed_table.index(row)
                row['transaction_type'] = 'issue'

    # after-the-fact surtype assignment
    if surtype_index != -1:
        for row in parsed_table[:surtype_index]:
            row['transaction_type'] = 'issue'
        for row in parsed_table[surtype_index + 1:]:
            row['transaction_type'] = 'redemption'

    # create data frame from table list of row dicts
    df = pd.DataFrame(parsed_table)

    # and pretty them up
    if re.search(r'TABLE I\s', row.get('table', '')):
        df = df.reindex(columns=['table', 'url', 'date', 'year_month', 'year', 'month', 'day', 'weekday', 'is_total', 'account', 'account_raw', 'close_today', 'open_today', 'open_mo', 'open_fy', 'footnote'])
        # check_for_nulls(df, "t1")
    elif re.search(r'TABLE II\s', row.get('table', '')):
        df = df.reindex(columns=['table', 'url', 'date', 'year_month', 'year', 'month', 'day', 'weekday', 'account', 'transaction_type', 'parent_item', 'is_total', 'is_net', 'item', 'item_raw', 'today', 'mtd', 'fytd', 'footnote'])
        if 'withdrawal' not in set(list(df['transaction_type'])):
            LOGGER.error('No withdrawal items in t2 for %s', df['date'][0])
        # check_for_nulls(df, "t2")
    elif re.search(r'TABLE III-A', row.get('table', '')):
        df = df.reindex(columns=['table', 'url', 'date', 'year_month', 'year', 'month', 'day', 'weekday', 'transaction_type', 'debt_type', 'parent_item', 'is_total', 'item', 'item_raw', 'today', 'mtd', 'fytd', 'footnote'])
        # check_for_nulls(df, "t3a")
    elif re.search(r'TABLE III-B', row.get('table', '')):
        df = df.reindex(columns=['table', 'url', 'date', 'year_month', 'year', 'month', 'day', 'weekday', 'transaction_type', 'parent_item', 'is_total', 'item', 'item_raw', 'today', 'mtd', 'fytd', 'footnote'])
        # check_for_nulls(df, "t3b")
    elif re.search(r'TABLE III-C', row.get('table', '')):
        df = df.reindex(columns=['table', 'url', 'date', 'year_month', 'year', 'month', 'day', 'weekday', 'is_total', 'parent_item', 'item', 'item_raw', 'close_today', 'open_today', 'open_mo', 'open_fy', 'footnote'])
        # check_for_nulls(df, "t3c")
    elif re.search(r'TABLE IV', row.get('table', '')):
        df = df.reindex(columns=['table', 'url', 'date', 'year_month', 'year', 'month', 'day', 'weekday', 'type', 'is_total', 'classification', 'classification_raw', 'today', 'mtd', 'fytd', 'footnote'])
        # check_for_nulls(df, "t4")
    elif re.search(r'TABLE V\s', row.get('table', '')):
        df = df.reindex(columns=['table', 'url', 'date', 'year_month', 'year', 'month', 'day', 'weekday', 'transaction_type', 'is_total', 'balance_transactions', 'depositary_type_a', 'depositary_type_b', 'depositary_type_c', 'total', 'footnote'])
        # check_for_nulls(df, "t5")
    elif re.search(r'TABLE VI', row.get('table', '')):
        df = df.reindex(columns=['table', 'url', 'date', 'year_month', 'year', 'month', 'day', 'weekday', 'refund_method', 'refund_type', 'refund_type_raw', 'today', 'mtd', 'fytd', 'footnote'])
        # check_for_nulls(df, "t6")

    return df


def main():
    parser = argparse.ArgumentParser(
        description='Script to parse "FMS fixie" files.')
    parser.add_argument(
        '-s', '--startdate', type=str, default=EARLIEST_DATE.format('YYYY-MM-DD'),
        help="""Start of date range over which to parse FMS fixies
             as an ISO-formatted string, i.e. YYYY-MM-DD.""")
    parser.add_argument(
        '-e', '--enddate', type=str, default=arrow.utcnow().shift(days=-1).format('YYYY-MM-DD'),
        help="""End of date range over which to download FMS fixies
             as an ISO-formatted string, i.e. YYYY-MM-DD.""")
    parser.add_argument(
        '--fixiedir', type=str, default=DEFAULT_FIXIE_DIR,
        help='Directory on disk from which fixies (raw text) are loaded.')
    parser.add_argument(
        '--dailycsvdir', type=str, default=DEFAULT_DAILY_CSV_DIR,
        help='Directory on disk to which parsed fixies (daily CSVs) are saved.')
    parser.add_argument(
        '--loglevel', type=int, default=20, choices=[10, 20, 30, 40, 50],
        help='Level of message to be logged; 20 => "INFO".')
    parser.add_argument(
        '--force', default=False, action='store_true',
        help="""If True, parse all fixies in [start_date, end_date], even if
             the resulting csvs already exist on disk in ``dailycsvdir``.
             Otherwise, only parse un-parsed fixies.""")
    args = parser.parse_args()

    LOGGER.setLevel(args.loglevel)

    # auto-make data directories, if not present
    for dir_ in (args.fixiedir, args.dailycsvdir):
        try:
            os.makedirs(dir_)
        except OSError:  # already exists
            continue

    # get all valid dates within range, and their corresponding fixie files
    all_dates = get_all_dates(args.startdate, args.enddate)
    if not all_dates:
        LOGGER.warning(
            'no valid dates in range [%s, %s]',
            args.startdate, args.enddate)
        return

    fixies_by_date = get_fixies_by_date(
        all_dates[0], all_dates[-1], data_dir=args.fixiedir)
    # if force is False, only parse fixies that haven't yet been parsed
    if args.force is False:
        daily_csv_dates = set(
            get_daily_csvs_by_date(
                all_dates[0], all_dates[-1], data_dir=args.dailycsvdir
                ).keys())
        if daily_csv_dates:
            fixies_by_date = {
                dt: fname for dt, fname in fixies_by_date.items()
                if dt not in daily_csv_dates}

    if not fixies_by_date:
        LOGGER.warning(
            'no un-parsed fixies in range [%s, %s]',
            args.startdate, args.enddate)
    else:
        LOGGER.info(
            'parsing %s fixies in range [%s, %s] and saving them to %s',
            len(fixies_by_date), args.startdate, args.enddate, args.dailycsvdir)
        fixie_fnames = (
            fname for _, fname in sorted(fixies_by_date.items(), key=itemgetter(0)))
        parse_all_fixies(fixie_fnames, args.dailycsvdir)


if __name__ == '__main__':
    sys.exit(main())
