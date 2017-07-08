from __future__ import absolute_import

import collections
import datetime
import logging
import os
import re

import arrow
import holidays

from .constants import DEFAULT_FIXIE_DIR, DEFAULT_DAILY_CSV_DIR, EARLIEST_DATE


LOGGER = logging.getLogger('utils')
LOGGER.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(name)s | %(levelname)s | %(message)s')
_handler.setFormatter(_formatter)
LOGGER.addHandler(_handler)


re_fname_date_str = re.compile(r'^(\d{6})(\d{2})_?([\w_]*?)(?:\.txt|\.csv)$')


def get_all_dates(start_date, end_date):
    """
    Get all dates between ``start_date`` and ``end_date`` that are neither
    holidays nor weekends.

    Args:
        start_date (str or datetime or :class:`arrow.Arrow`)
        end_date (str or datetime or :class:`arrow.Arrow`)

    Returns:
        Tuple[:class:`arrow.Arrow`]
    """
    start_date = arrow.get(start_date)
    end_date = arrow.get(end_date) if end_date else start_date
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


def get_fixies_by_date(start_date, end_date, data_dir=DEFAULT_FIXIE_DIR):
    """
    Args:
        start_date (:class:`arrow.Arrow`)
        end_date (:class:`arrow.Arrow`)
        data_dir (str)

    Returns:
        Dict[:class:`arrow.Arrow`, str]
    """
    start_date_str = start_date.format('YYMMDD')
    end_date_str = end_date.format('YYMMDD')
    fnames_by_date = {}
    for fname in os.listdir(data_dir):
        match = re_fname_date_str.search(fname)
        # filter out the cruft
        if not match:
            continue
        fname_date_str = match.group(1)
        if not start_date_str <= fname_date_str <= end_date_str:
            continue
        fname_date = arrow.get(datetime.datetime.strptime(fname_date_str, '%y%m%d'))
        fnames_by_date[fname_date] = os.path.join(data_dir, fname)

    return fnames_by_date


def get_daily_csvs_by_date(start_date, end_date, data_dir=DEFAULT_DAILY_CSV_DIR):
    """
    Args:
        start_date (:class:`arrow.Arrow`)
        end_date (:class:`arrow.Arrow`)
        data_dir (str)

    Returns:
        Dict[str, List[str]]
    """
    start_date_str = start_date.format('YYMMDD')
    end_date_str = end_date.format('YYMMDD')
    fnames_by_date = collections.defaultdict(dict)
    for fname in os.listdir(data_dir):
        match = re_fname_date_str.search(fname)
        # filter out the cruft
        if not match:
            continue
        fname_date_str = match.group(1)
        table_key = match.group(3)
        if not start_date_str <= fname_date_str <= end_date_str:
            continue
        fname_date = arrow.get(datetime.datetime.strptime(fname_date_str, '%y%m%d'))
        fnames_by_date[fname_date][table_key] = os.path.join(data_dir, fname)

    return dict(fnames_by_date)


def get_date_from_fname(fname):
    """
    Args:
        fname (str)

    Returns:
        :class:`datetime.date`
    """
    match = re_fname_date_str.search(fname)
    if not match:
        raise ValueError('invalid fname: "{}"'.format(fname))
    date_str = match.group(1)
    return datetime.datetime.strptime(date_str, '%y%m%d').date()
