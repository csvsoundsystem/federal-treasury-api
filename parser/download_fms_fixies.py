#!/usr/bin/env python
from __future__ import print_function

import argparse
import datetime
import io
import logging
import os
import sys
import time

import arrow
import holidays
import pandas as pd
import requests


BASE_URL = 'https://www.fms.treas.gov/fmsweb/viewDTSFiles'
SAVE_DIR = os.path.join('..', 'data', 'fixie')

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(name)s | %(levelname)s | %(message)s')
_handler.setFormatter(_formatter)
LOGGER.addHandler(_handler)

EARLIEST_DATE = arrow.get('2005-06-09')
""":class:`arrow.Arrow`: Earliest date of available fixie files. Note that PDFs
*are* available, for the brave soul who wants to parse them."""


def download_fixies(start_date, end_date=None, save_dir=SAVE_DIR):
    """
    Download FMS fixie files from the FMS website for all non-weekend, non-
    holiday dates between ``start_date`` and ``end_date``.

    Args:
        start_date (datetime or str)
        end_date (datetime or str)
        save_dir (str)
    """
    start_date = arrow.get(start_date)
    end_date = arrow.get(end_date) if end_date else start_date
    all_dates = get_all_dates(start_date, end_date)
    LOGGER.info(
        'downloading FMS fixies from %s to %s!',
        all_dates[0].date(), all_dates[-1].date())

    fnames = generate_fixie_fnames(all_dates)
    request_all_fixies(fnames, save_dir)


def get_all_dates(start_date, end_date):
    """
    Get all dates between ``start_date`` and ``end_date`` that are neither
    holidays nor weekends.

    Args:
        start_date (:class:`arrow.Arrow`)
        end_date (:class:`arrow.Arrow`)

    Returns:
        Tuple[:class:`arrow.Arrow`]
    """
    # sanity check the date range
    if start_date < EARLIEST_DATE:
        start_date = EARLIEST_DATE
        LOGGER.warning(
            'start date "%s" before earliest available date; setting equal to "%s"',
            start_date, EARLIEST_DATE)
    if start_date > end_date:
        start_date, end_date = end_date, start_date
        LOGGER.warning(
            'start date "%s" before end date "%s"; swapping the dates',
            start_date, end_date)
    # no fixies on holidays or weekends; remove them
    us_holidays = holidays.UnitedStates(
        years=range(start_date.year, end_date.year + 1),
        observed=True)
    return tuple(dt for dt in arrow.Arrow.range('day', start_date, end_date)
                 if dt.isoweekday() < 6 and dt.date() not in us_holidays)


def generate_fixie_fnames(dates):
    """
    Generate likely fixie filenames for each date in ``dates``. Fnames are
    constructed by combining the date formatted as 'YYMMDD', a zero-padded digit
    string like '00', and the filetype, '.txt'.

    Args:
        dates (Iterable[:class:`arrow.Arrow`])

    Yields:
        Tuple[str]
    """
    suffixes = ('00.txt', '01.txt', '02.txt', '03.txt')
    for dt in dates:
        yield tuple(dt.format('YYMMDD') + suffix for suffix in suffixes)


def request_all_fixies(all_fnames, save_dir):
    """
    Args:
        all_fnames (Iterable[Tuple[str]])
    """
    for fnames in all_fnames:
        time.sleep(0.1)
        success = False
        for fname in fnames:
            fixie = request_fixie(fname)
            if fixie:
                filepath = os.path.join(save_dir, fname)
                with io.open(filepath, mode='wb') as f:
                    f.write(fixie)
                LOGGER.info('%s fixie saved to %s', fname, filepath)
                success = True
                break
        if success is False:
            LOGGER.warning(
                '%s fixie (%s) not found',
                fnames[0],
                str(datetime.datetime.strptime(fname[:6], '%y%m%d').date()))


def request_fixie(fname):
    """
    Request fixie files from FMS server, checking in 2 different directories
    where they are likely to be stored.

    Args:
        fname (str)

    Returns:
        str or None
    """
    for dir_ in ('a', 'w'):
        response = requests.get(BASE_URL, params={'dir': 'a', 'fname': fname})
        if response.status_code == 200:
            return response.text
    return None


def main():
    parser = argparse.ArgumentParser(
        description="""Script to download "FMS fixie" files for all non-weekend,
                    non-holiday dates between ``startdate`` and ``enddate``.""")
    parser.add_argument(
        '-s', '--startdate', type=str, default=EARLIEST_DATE.format('YYYY-MM-DD'),
        help="""Start of date range over which to download FMS fixies
             as an ISO-formatted string, i.e. YYYY-MM-DD.""")
    parser.add_argument(
        '-e', '--enddate', type=str, default=arrow.utcnow().format('YYYY-MM-DD'),
        help="""End of date range over which to download FMS fixies
             as an ISO-formatted string, i.e. YYYY-MM-DD.""")
    parser.add_argument(
        '--savedir', type=str, default=SAVE_DIR,
        help='Directory on disk to which fixies will be saved.')
    args = parser.parse_args()

    download_fixies(args.startdate, end_date=args.enddate, save_dir=args.savedir)


if __name__ == '__main__':
    sys.exit(main())
