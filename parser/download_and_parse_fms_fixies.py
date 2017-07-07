#!/usr/bin/env python
from __future__ import division, print_function

import argparse
import datetime
import logging
import os
import re
import sqlite3
import sys

import arrow
import pandas as pd

from .constants import (DEFAULT_FIXIE_DIR,
                        DEFAULT_DAILY_CSV_DIR,
                        DEFAULT_LIFETIME_CSV_DIR,
                        EARLIEST_DATE,
                        PARSER_DIR)
from .download_fms_fixies import generate_fixie_fnames, request_all_fixies
from .parse_fms_fixies import parse_fixie
from .utils import get_all_dates, get_fixies_by_date, get_daily_csvs_by_date


LOGGER = logging.getLogger('download_and_parse_fms_fixies')
LOGGER.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(name)s | %(levelname)s | %(message)s')
_handler.setFormatter(_formatter)
LOGGER.addHandler(_handler)


def main():

    parser = argparse.ArgumentParser(
        description="""Script to download "FMS fixie" files for all non-weekend,
                    non-holiday dates between ``startdate`` and ``enddate``.""")
    parser.add_argument(
        '-s', '--startdate', type=str, default=EARLIEST_DATE.format('YYYY-MM-DD'),
        help="""Start of date range over which to download FMS fixies
             as an ISO-formatted string, i.e. YYYY-MM-DD.""")
    parser.add_argument(
        '-e', '--enddate', type=str, default=arrow.utcnow().shift(days=-1).format('YYYY-MM-DD'),
        help="""End of date range over which to download FMS fixies
             as an ISO-formatted string, i.e. YYYY-MM-DD.""")
    parser.add_argument(
        '--fixiedir', type=str, default=DEFAULT_FIXIE_DIR,
        help='Directory on disk to which fixies will be saved.')
    parser.add_argument(
        '--dailycsvdir', type=str, default=DEFAULT_DAILY_CSV_DIR,
        help='Directory on disk to which daily csvs will be saved.')
    parser.add_argument(
        '--lifetimecsvdir', type=str, default=DEFAULT_LIFETIME_CSV_DIR,
        help='Directory on disk to which lifetime csvs will be saved.')
    parser.add_argument(
        '--loglevel', type=int, default=20, choices=[10, 20, 30, 40, 50],
        help='Level of message to be logged; 20 => "INFO".')
    parser.add_argument(
        '--force', default=False, action='store_true',
        help="""If true, download all fixies in [start_date, end_date], even if
             the resulting files already exist on disk in ``datadir``.
             Otherwise, only download un-downloaded fixies.""")
    args = parser.parse_args()

    LOGGER.setLevel(args.loglevel)

    # auto-make data directories, if not present
    for dir_ in (args.fixiedir, args.dailycsvdir, args.lifetimecsvdir):
        try:
            os.makedirs(dir_)
        except OSError:  # already exists
            continue

    # get all valid dates within range
    all_dates = get_all_dates(args.startdate, args.enddate)
    if not all_dates:
        LOGGER.warning(
            'no valid dates in range [%s, %s]',
            args.startdate, args.enddate)
        return

    # if force is False, only download fixies that haven't yet been downloaded
    if args.force is False:
        fixie_dates = set(
            get_fixies_by_date(
                all_dates[0], all_dates[-1], data_dir=args.fixiedir
                ).keys())
        if fixie_dates:
            fixie_dates = sorted(set(all_dates).difference(fixie_dates))
    else:
        fixie_dates = all_dates
    if not fixie_dates:
        LOGGER.warning(
            'no un-requested fixies in range [%s, %s]',
            args.startdate, args.enddate)
    else:
        LOGGER.info(
            'requesting %s fixies and saving them to %s',
            len(fixie_dates), args.fixiedir)
        fixie_fnames = generate_fixie_fnames(fixie_dates)
        request_all_fixies(fixie_fnames, args.fixiedir)

    # get all fixie files for date range
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
            'parsing %s fixies and saving them to %s',
            len(fixies_by_date), args.dailycsvdir)
        fixie_fnames = (
            fname for _, fname in sorted(fixies_by_date.items(), key=itemgetter(0)))
        parse_all_fixies(fixie_fnames, args.dailycsvdir)

    return

    # HERE BE DRAGONS #

    # test for existence of downloaded fixies
    test_fixies = sorted(f for f in os.listdir(FIXIE_DIR) if f.endswith('.txt'))
    # if none, start from THE BEGINNING
    if len(test_fixies) == 0:
        start_date = datetime.date(2005, 6, 9)
    # else start from last available fixie date
    else:
        start_date = parse_fms_fixies.get_date_from_fname(test_fixies[-1])
    # always end with today
    end_date = datetime.date.today()

    # download all teh fixies!
    download_fixies(start_date, end_date)

    # check all downloaded fixies against all parsed csvs
    downloaded_files = set([fixie.split('.')[0] for fixie in os.listdir(FIXIE_DIR)
                            if fixie.endswith('.txt')])

    def parsed_files():
        return set([csv.split('_')[0] for csv in os.listdir(DAILY_CSV_DIR) if csv.endswith('.csv')])

    # fixies that have not yet been parsed into csvs
    new_files = sorted(list(downloaded_files.difference(parsed_files())))

    # parse all teh fixies!
    for f in new_files:
        fname = os.path.join(FIXIE_DIR, f+'.txt')
        dfs = parse_fms_fixies.parse_file(fname, verbose=False)

        # each table for each date stored in separate csv files
        for df in dfs.values():
            try:
                t_name = df.ix[0, 'table']
                t_name_match = re.search(r'TABLE [\w-]+', t_name)
                t_name_short = re.sub(r'-| ', '_', t_name_match.group().lower())
            except Exception as e:
                print('***ERROR: tables failed to parse!', e)
                # go on
                continue

            daily_csv = os.path.join(DAILY_CSV_DIR, f.split('.')[0]+'_'+t_name_short+'.csv')
            df.to_csv(daily_csv, index=False, header=True, encoding='utf-8', na_rep='')

    # iterate over all fms tables
    for i in ['i', 'ii', 'iii_a', 'iii_b', 'iii_c', 'iv', 'v', 'vi']:

        # create the lifetime csv files it they don't exist
        lifetime_csv = os.path.join(LIFETIME_CSV_DIR, 'table_'+str(i)+'.csv')

        # if it doesn't exist
        if not os.path.isfile(lifetime_csv):
            lifetime = open(lifetime_csv, 'ab')
            # add the header
            lifetime.write(open(os.path.join(DAILY_CSV_DIR, list(parsed_files())[0]+'_table_'+str(i)+'.csv')).readline())
            lifetime.close()

        # append new csvs to lifetime csvs
        for f in new_files:

            # we have no idea why it's giving us a blank file
            if len(f) == 0:
                continue

            daily_csv = os.path.join(DAILY_CSV_DIR, f.split('.')[0]+'_table_'+str(i)+'.csv')
            if not os.path.isfile(daily_csv):
                continue

            lifetime = open(lifetime_csv, 'ab')
            daily = open(daily_csv, 'rb')

            daily.readline()  # burn header
            for line in daily:
                lifetime.write(line)
            daily.close()

    TABLES = [
        {'raw-table': 'i', 'new-table': 't1'},
        {'raw-table': 'ii', 'new-table': 't2'},
        {'raw-table': 'iii_a', 'new-table': 't3a'},
        {'raw-table': 'iii_b', 'new-table': 't3b'},
        {'raw-table': 'iii_c', 'new-table': 't3c'},
        {'raw-table': 'iv', 'new-table': 't4'},
        {'raw-table': 'v', 'new-table': 't5'},
        {'raw-table': 'vi', 'new-table': 't6'},
        ]

    # delete the db and promptly rewrite it from csvs
    print("INFO: building sqlite database")
    db = os.path.join('..', 'data', 'treasury_data.db')
    os.system("rm " + db)

    connection = sqlite3.connect(db)
    connection.text_factory = str  # bad, but pandas doesn't work otherwise

    for table in TABLES:
        df = pandas.read_csv(
            os.path.join('..', 'data', 'lifetime_csv', 'table_%s.csv' % table['raw-table']))

        # WARNING SERIOUS HACKS FOLLOW #
        # FILTER OUT TABLE 5 AFTER  2012-04-02 - HACK BUT WORKS FOR NOW #
        if table['new-table'] == "t5":
            print("INFO: filtering out invalid dates for TABLE V (deprecated as of 2012-04-02) ")
            table_v_end = datetime.date(2012, 4, 2)
            df.date = df.date.apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").date())
            df = df[df.date < table_v_end]

        # pandas.io.sql.write_frame(df, table['new-table'], connection)
        df.to_sql(table['new-table'], connection, index=False)

    # Commit
    connection.commit()

    csv_txt = r"""
      ,----..    .--.--.
     /   /   \  /  /    '.       ,---.
    |   :     :|  :  /`. /      /__./|
    .   |  ;. /;  |  |--`  ,---.;  ; |
    .   ; /--` |  :  ;_   /___/ \  | |
    ;   | ;     \  \    `.\   ;  \ ' |
    |   : |      `----.   \\   \  \: |
    .   | '___   __ \  \  | ;   \  ' .
    '   ; : .'| /  /`--'  /  \   \   '
    '   | '/  :'--'.     /    \   `  ;
    |   :    /   `--'---'      :   \ |
     \   \ .'                   '---"
      `---`
    """
    soundsystem_txt = r"""
    .-. .-. . . . . .-. .-. . . .-. .-. .-. .  .
    `-. | | | | |\| |  )`-.  |  `-.  |  |-  |\/|
    `-' `-' `-' ' ` `-' `-'  `  `-'  '  `-' '  `
    """
    welcome_msg = r"""
    Everything you just downloaded is in the data/ directory.
    The raw files are in data/fixie.
    They were parsed and converted to CSVs in the data/daily_csv directory.
    These are combined by table in the data/lifetime_csv directory.
    Those tables were made into a SQLite database at data/treasury_data.db, which you can load using your favorite SQLite viewer.
    If you have any questions, check out http://treasury.io for usage and a link to the support Google Group.
    """
    print(csv_txt)
    print(soundsystem_txt)
    print('*http://csvsoundsystem.com/')
    print(welcome_msg)


if __name__ == '__main__':
    print(os.getcwd() == PARSER_DIR)
    sys.exit(main())
