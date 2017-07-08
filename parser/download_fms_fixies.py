#!/usr/bin/env python
from __future__ import absolute_import, print_function

import argparse
import datetime
import io
import logging
import os
import random
import sys
import time

import arrow
import pandas as pd
import requests

from .constants import DEFAULT_FIXIE_DIR, EARLIEST_DATE
from .utils import get_all_dates, get_fixies_by_date


LOGGER = logging.getLogger('download_fms_fixies')
LOGGER.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(name)s | %(levelname)s | %(message)s')
_handler.setFormatter(_formatter)
LOGGER.addHandler(_handler)

BASE_URL = 'https://www.fms.treas.gov/fmsweb/viewDTSFiles'


def download_fixies(start_date, end_date=None, data_dir=DEFAULT_FIXIE_DIR):
    """
    Download FMS fixie files from the FMS website for all non-weekend, non-
    holiday dates between ``start_date`` and ``end_date``.

    Args:
        start_date (datetime or str)
        end_date (datetime or str)
        data_dir (str)
    """
    all_dates = get_all_dates(start_date, end_date)
    LOGGER.info(
        'downloading FMS fixies from %s to %s!',
        all_dates[0].date(), all_dates[-1].date())

    fnames = generate_fixie_fnames(all_dates)
    request_all_fixies(fnames, data_dir)


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


def request_all_fixies(all_fnames, data_dir):
    """
    Args:
        all_fnames (Iterable[Tuple[str]])
        data_dir (str)
    """
    for fnames in all_fnames:
        time.sleep(0.1 + 0.1 * random.random())
        success = False
        for fname in fnames:
            fixie = request_fixie(fname)
            if fixie:
                filepath = os.path.join(data_dir, fname)
                with io.open(filepath, mode='wb') as f:
                    f.write(fixie)
                LOGGER.info('%s fixie saved to %s', fname, filepath)
                success = True
                break
        if success is False:
            LOGGER.warning(
                '%s fixie (%s) not available',
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
        response = requests.get(BASE_URL, params={'dir': dir_, 'fname': fname})
        if response.status_code == 200:
            return response.text
    return None


def main():
    parser = argparse.ArgumentParser(
        description="""Script to download "FMS fixie" files for all non-weekend,
                    non-holiday dates between ``startdate`` and ``enddate``.""")
    parser.add_argument(
        '-s', '--startdate', type=str, default=arrow.utcnow().shift(days=-8).format('YYYY-MM-DD'),
        help="""Start of date range over which to download FMS fixies
             as an ISO-formatted string, i.e. YYYY-MM-DD.""")
    parser.add_argument(
        '-e', '--enddate', type=str, default=arrow.utcnow().shift(days=-1).format('YYYY-MM-DD'),
        help="""End of date range over which to download FMS fixies
             as an ISO-formatted string, i.e. YYYY-MM-DD.""")
    parser.add_argument(
        '--fixiedir', type=str, default=DEFAULT_FIXIE_DIR,
        help='Directory on disk to which fixies (raw text) are saved.')
    parser.add_argument(
        '--loglevel', type=int, default=20, choices=[10, 20, 30, 40, 50],
        help='Level of message to be logged; 20 => "INFO".')
    parser.add_argument(
        '--force', default=False, action='store_true',
        help="""If True, download all fixies in [start_date, end_date], even if
             the resulting files already exist on disk in ``datadir``.
             Otherwise, only download un-downloaded fixies.""")
    args = parser.parse_args()

    LOGGER.setLevel(args.loglevel)

    # auto-make data directory, if not present
    try:
        os.makedirs(args.fixiedir)
    except OSError:  # already exists
        pass

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


if __name__ == '__main__':
    sys.exit(main())
