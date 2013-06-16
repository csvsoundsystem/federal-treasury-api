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
