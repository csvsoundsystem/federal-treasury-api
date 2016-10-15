#!/usr/bin/env python
from __future__ import print_function

import argparse
from datetime import datetime
import io
import logging
import os
import sys
from time import sleep

import arrow
import holidays
import pandas as pd
import requests


BASE_URL = 'https://www.fms.treas.gov/fmsweb/viewDTSFiles'
SAVE_DIR = os.path.join('..', 'data', 'fixie')

LOGGER = logging.getLogger('download_fms_fixies')
LOGGER.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(name)s | %(levelname)s | %(message)s')
_handler.setFormatter(_formatter)
LOGGER.addHandler(_handler)

EARLIEST_DATE = arrow.get('2005-06-09')
"""fixie files not available before this date; PDFs *are* available,
for the brave soul who wants to parse them"""


def get_all_dates(start_date, end_date):
    """
    Get all dates between ``start_date`` and ``end_date`` that are neither
    holidays nor weekends.

    Args:
        start_date (:class:``arrow.Arrow``)
        end_date (:class:``arrow.Arrow``)

    Returns:
        Tuple[:class:``arrow.Arrow``]
    """
    # sanity check the date range
    if start_date < EARLIEST_DATE:
        start_date = EARLIEST_DATE
        LOGGER.warning(
            'start date "{}" before earliest available date; setting equal to "{}"'.format(
                start_date, EARLIEST_DATE))
    if start_date > end_date:
        start_date, end_date = end_date, start_date
        LOGGER.warning(
            'start date "{}" and end date "{}" swapped'.format(
                start_date, end_date))
    # no fixies on holidays or weekends; remove them
    us_holidays = holidays.UnitedStates(
        years=range(start_date.year, end_date.year + 1),
        observed=True)
    return tuple(dt for dt in arrow.Arrow.range('day', start_date, end_date)
                 if dt.isoweekday() < 6 and dt.date() not in us_holidays)


def request_fixie(fname):
    """
    Args:
        fname (str)
    """
    # fixie files may be served from different directories...
    for dir_ in ('a', 'w'):
        response = requests.get(
            BASE_URL, params={'dir': 'a', 'fname': fname})
        if response.status_code == 200:
            return response.text
    return None


def request_all_fixies(fnames):
    """
    Args:
        fnames (List[str])
    """
    for fname in fnames:
        sleep(0.1)
        alt_fnames = [fname]
        alt_fnames.extend(fname[:-5] + i +'.txt' for i in ['1', '2', '3'])
        for alt_fname in alt_fnames:
            fixie = request_fixie(alt_fname)
            if fixie:
                filepath = os.path.join(SAVE_DIR, alt_fname)
                with io.open(filepath, mode='wb') as f:
                    f.write(fixie)
                LOGGER.info('fixie saved to {}'.format(filepath))
                break
        if fixie is None:
            LOGGER.warning('{} fixie ({}) not found'.format(
                fname, str(datetime.strptime(fname[:6], '%y%m%d').date())))


def download_fixies(start_date, end_date=None):
    """
    Args:
        start_date (datetime or str)
        end_date (datetime or str)
    """
    start_date = arrow.get(start_date)
    end_date = arrow.get(end_date) if end_date else start_date
    all_dates = get_all_dates(start_date, end_date)
    LOGGER.info('Downloading FMS fixies from {} to {}!'.format(
        all_dates[0].date(), all_dates[-1].date()))

    fnames = [dt.format('YYMMDD') + '00.txt' for dt in all_dates]
    request_all_fixies(fnames)


def main():
    parser = argparse.ArgumentParser(description='Download FMS fixies.')
    parser.add_argument(
        '-s', '--startdate', type=str, default=EARLIEST_DATE.format('YYYY-MM-DD'),
        help="""start of date range over which to download FMS fixies
             as an ISO-formatted string, i.e. YYYY-MM-DD""")
    parser.add_argument(
        '-e', '--enddate', type=str, default=arrow.utcnow().format('YYYY-MM-DD'),
        help="""end of date range over which to download FMS fixies
             as an ISO-formatted string, i.e. YYYY-MM-DD""")

    args = vars(parser.parse_args())

    download_fixies(args['startdate'], args['enddate'])


if __name__ == '__main__':
    sys.exit(main())
