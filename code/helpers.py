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
def check_parse(fixie_basename):
    observed = parse_file(os.path.join('fixtures', fixie_basename + '.txt'), 'r')
    expected = parsed_file_from_json(open(os.path.join('fixtures', fixie_basename + '.json'), 'r'))
    for table_number in expected.keys():
        for column in expected[table_number].keys():
            print observed[table_number]['footnote']
            print expected[table_number]['footnote']
            n.assert_dict_equal(
                observed[table_number][column].to_dict(),
                expected[table_number][column].to_dict()
            )
