import os, datetime
import StringIO

import nose.tools as n
import pandas

from parse_fms_fixies_2 import parse_file

def check_parse(fixie_basename):
    observed_dict = parse_file(os.path.join('fixtures', fixie_basename + '.txt'), 'r')
    observed_csv  = {i:StringIO.StringIO() for i in observed_dict.keys()}
    for i in observed_csv.keys():
        observed_dict[i].to_csv(observed_csv[i],
			index=False, header=True, encoding='utf-8', na_rep='')
        observed_csv[i] = observed_csv[i].getvalue()

    expected_csv  = {i:open(os.path.join('fixtures', '%s_t%d.csv' % (fixie_basename, i))).read() for i in range(1,9)}

    for i in expected_csv.keys():
        n.assert_list_equal(
            observed_csv[i].split('\n'),
            expected_csv[i].split('\n'),
        )

    return observed_csv, expected_csv
