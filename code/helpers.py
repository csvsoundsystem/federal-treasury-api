import os, datetime

import nose.tools as n
import numpy.testing as nt
import numpy
import pandas

from parse_fms_fixies_2 import parse_file

NA_FILL = {
    numpy.dtype('O'): '',
    numpy.dtype('float64'): 0,
    numpy.dtype('int64'): 0,
}
def fillna(series):
    return series.fillna(NA_FILL[series.dtype])

def check_parse(fixie_basename):
    observed = parse_file(os.path.join('fixtures', fixie_basename + '.txt'), 'r')
    expected = {i:pandas.read_csv(os.path.join('fixtures', '%s_t%d.csv' % (fixie_basename, i))) for i in range(1,9)}
    for table_number in expected.keys():
        expected[table_number]['date'] = expected[table_number]['date'].apply(lambda d: datetime.date(*map(int, d.split('-'))))

    for table_number in expected.keys():
        for column_name in expected[table_number].columns:
            print column_name
            observed_series = observed[table_number][column_name]
            expected_series = expected[table_number][column_name]
            observed_list = list(observed_series)
            expected_list = list(expected_series)

            if observed_series.name in {'open_today','open_mo','open_fy','close_today','today','mtd','fytd'}:
                observed_list = map(int, observed_list)

            # Hack to deal with NAs, which are floats and annoying to compare.
            observed_series = fillna(observed_series)
            expected_series = fillna(expected_series)
            observed_list = list(observed_series)
            expected_list = list(expected_series)

            n.assert_list_equal(observed_list, expected_list)
