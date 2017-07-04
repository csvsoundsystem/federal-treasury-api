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
