import json, datetime

import pandas

def unstring_stuff(d):
    d = {int(k):v for k,v in d.items()}
    return d

def string_stuff(d):
    d = {str(k):v for k,v in d.items()}
    return d

def parsed_file_to_json(parsed_file_dict, fp):
    d = string_stuff(parsed_file_dict)
    for col in d.keys():
        d[col] = string_stuff(d[col].to_dict())
        for i in d[col]['date'].keys():
            d[col]['date'][i] = d[col]['date'][i].toordinal()
    json.dump(d, fp)

def parsed_file_from_json(parsed_file_json_fp):
    d = unstring_stuff(json.load(parsed_file_json_fp))
    for table in d.keys():
        for i in d[table]['date'].keys():
            d[table]['date'][i] = datetime.date.fromordinal(d[table]['date'][i])
        for col in d[table]:
            d[table][col] = (unstring_stuff(d[table][col]))
        d[table] = pandas.DataFrame(d[table])
    return d

import os
from parse_fms_fixies_2 import parse_file
import nose.tools as n
import numpy.testing as nt
import numpy
NA = {
    numpy.dtype('O'): '',
    numpy.dtype('float64'): 0,
    numpy.dtype('int64'): 0,
}
def check_parse(fixie_basename):
    observed = parse_file(os.path.join('fixtures', fixie_basename + '.txt'), 'r')
    expected = parsed_file_from_json(open(os.path.join('fixtures', fixie_basename + '.json'), 'r'))
    for table_number in expected.keys():
        for column_name in expected[table_number].columns:
            # Quite a hack
            observed_series = observed[table_number][column_name].fillna(NA[observed[table_number][column_name].dtype])
            expected_series = expected[table_number][column_name].fillna(NA[observed[table_number][column_name].dtype])
            n.assert_list_equal(*map(list, [observed_series, expected_series]))
