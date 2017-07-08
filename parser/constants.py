import os

import arrow


EARLIEST_DATE = arrow.get('2005-06-09')
"""
:class:`arrow.Arrow`: Earliest date of available fixie files. Note that PDFs
*are* available, for the brave soul who wants to parse them.
"""

PARSER_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_DIR = os.path.abspath(os.path.join(PARSER_DIR, '..', 'data'))
DEFAULT_FIXIE_DIR = os.path.join(DEFAULT_DATA_DIR, 'fixie')
DEFAULT_DAILY_CSV_DIR = os.path.join(DEFAULT_DATA_DIR, 'daily_csv')
DEFAULT_LIFETIME_CSV_DIR = os.path.join(DEFAULT_DATA_DIR, 'lifetime_csv')

TABLE_KEYS = (
    'table_i',
    'table_ii',
    'table_iii_a',
    'table_iii_b',
    'table_iii_c',
    'table_iv',
    'table_v',
    'table_vi',
    )

DB_TABLE_NAMES = (
    't1',
    't2',
    't3a',
    't3b',
    't3c',
    't4',
    't5',
    't6',
    )
