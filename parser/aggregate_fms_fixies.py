#!/usr/bin/env python
from __future__ import absolute_import, print_function

import argparse
import json
import logging
from operator import itemgetter
import os
import sqlite3
import sys

import arrow
import pandas as pd

from constants import (DEFAULT_DAILY_CSV_DIR, DEFAULT_LIFETIME_CSV_DIR,
                        DEFAULT_DATA_DIR, EARLIEST_DATE,
                        DB_TABLE_NAMES, TABLE_KEYS)
from utils import get_all_dates, get_daily_csvs_by_date


LOGGER = logging.getLogger('aggregate_fms_fixies')
LOGGER.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(name)s | %(levelname)s | %(message)s')
_handler.setFormatter(_formatter)
LOGGER.addHandler(_handler)


def aggregate_table(table_key, lifetimecsvdir, daily_csvs_by_date, force):
    """
    Args:
        table_key (str): Unique table identifier; see :obj:`TABLE_KEYS`.
        lifetimecsvdir (str)
        daily_csvs_by_date (List[Tuple[:class:`arrow.Arrow`, str]])
        force (bool)
    """
    lifetime_csv_fname = os.path.join(lifetimecsvdir, table_key + '.csv')
    # write a new lifetime file?
    if not os.path.isfile(lifetime_csv_fname) or force is True:
        lifetime_csv_dates = set()
        first_mode = 'w'
    # append to existing lifetime file?
    else:
        lifetime_csv_dates = set(
            pd.read_csv(lifetime_csv_fname, usecols=['date'])['date']
            .unique())
        first_mode = 'a'

    is_first = True
    for daily_csv_date, fnames in daily_csvs_by_date:
        if daily_csv_date.format('YYYY-MM-DD') in lifetime_csv_dates:
            LOGGER.debug(
                '%s %s table already aggregated -- skipping...',
                daily_csv_date, table_key)
        df = pd.read_csv(fnames[table_key], header=0)
        if is_first is True:
            df.to_csv(lifetime_csv_fname, mode=first_mode, header=True, index=False)
            is_first = False
        else:
            df.to_csv(lifetime_csv_fname, mode='a', header=False, index=False)


def build_db(dbfile, lifetimecsvdir):
    """
    Args:
        dbfile (str)
        lifetimecsvdir (str)
    """
    os.remove(dbfile)

    connection = sqlite3.connect(dbfile)
    # bad, but pandas doesn't work otherwise (TODO: check this)
    # true, but the perfect is the enemy of the good
    connection.text_factory = str

    for table_key, table_name in zip(TABLE_KEYS, DB_TABLE_NAMES):

        lifetime_csv_fname = os.path.join(lifetimecsvdir, table_key + '.csv')
        if not os.path.isfile(lifetime_csv_fname):
            LOGGER.warning(
                'lifetime CSV %s does not exist -- skipping db table build...',
                lifetime_csv_fname)
        df = pd.read_csv(lifetime_csv_fname, header=0)

        # HACK: filter out Table V after 2012-04-02
        # TODO: check with cezary podkul about this
        if table_name == 't5':
            LOGGER.debug(
                'filtering out invalid dates for TABLE V (deprecated as of 2012-04-02)')
            max_date = arrow.get('2012-04-02').date()
            df['date'] = df['date'].map(lambda x: arrow.get(x).date())
            df = df.loc[df['date'] < max_date, :]

        df.to_sql(table_name, connection, index=False)

    connection.commit()


def main():
    parser = argparse.ArgumentParser(
        description='Script to aggregate parsed "FMS fixie" files.')
    parser.add_argument(
        '-s', '--startdate', type=str, default=EARLIEST_DATE.format('YYYY-MM-DD'),
        help="""Start of date range over which to parse FMS fixies
             as an ISO-formatted string, i.e. YYYY-MM-DD.""")
    parser.add_argument(
        '-e', '--enddate', type=str, default=arrow.utcnow().shift(days=-1).format('YYYY-MM-DD'),
        help="""End of date range over which to download FMS fixies
             as an ISO-formatted string, i.e. YYYY-MM-DD.""")
    parser.add_argument(
        '--dailycsvdir', type=str, default=DEFAULT_DAILY_CSV_DIR,
        help='Directory on disk from which parsed fixies (daily CSVs) are loaded.')
    parser.add_argument(
        '--lifetimecsvdir', type=str, default=DEFAULT_LIFETIME_CSV_DIR,
        help='Directory on disk to which aggregated fixies (lifetime CSVs) are saved.')
    parser.add_argument(
        '-db', '--dbfile', type=str,
        default=os.path.join(DEFAULT_DATA_DIR, 'treasury_data.db'),
        help="""Write aggregated fixies (lifetime CSVs) to the SQL database file
             given here, provided the ``nodb`` flag is not specified.
             NOTE: DB file is overwritten in its entirety every time.""")
    parser.add_argument(
        '--loglevel', type=int, default=20, choices=[10, 20, 30, 40, 50],
        help='Level of message to be logged; 20 => "INFO".')
    parser.add_argument(
        '--nodb', default=False, action='store_true',
        help="""If True, don't bother (over)writing the SQL database file given
             in ``dbfile``.""")
    parser.add_argument(
        '--force', default=False, action='store_true',
        help="""If True, aggregate all parsed fixies in [start_date, end_date],
             overwriting any existing lifetime CSVs if they already exist on disk
             in ``lifetimecsvdir``. Otherwise, only aggregate un-aggregated fixies.""")
    args = parser.parse_args()

    LOGGER.setLevel(args.loglevel)

    # auto-make data directories, if not present
    for dir_ in (args.dailycsvdir, args.lifetimecsvdir):
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

    # get all parsed fixies within range, and sort them by date
    daily_csvs_by_date = sorted(
        get_daily_csvs_by_date(
            all_dates[0], all_dates[-1], data_dir=args.dailycsvdir).items(),
        key=itemgetter(0))

    if not daily_csvs_by_date:
        LOGGER.warning(
            'no parsed fixies in range [%s, %s]',
            args.startdate, args.enddate)
    else:
        # iterate over lifetime tables, adding corresponding daily rows as needed
        for table_key in TABLE_KEYS:
            LOGGER.info(
                'aggregating parsed fixies for %s in range [%s, %s]',
                table_key, args.startdate, args.enddate)
            aggregate_table(
                table_key, args.lifetimecsvdir, daily_csvs_by_date, args.force)

    # build a sqlite database of aggregated tables?
    if args.nodb is False:
        LOGGER.info(
            'building sqlite db file of aggregated tables at %s',
            args.dbfile)
        build_db(args.dbfile, args.lifetimecsvdir)


if __name__ == '__main__':
    sys.exit(main())
