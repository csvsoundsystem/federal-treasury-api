#!/usr/bin/env python
# Tested by Tom on Python 2.7.5 and Python 3.3.1 running on Arch Linux
import json
import datetime
from requests import get
from postmark import email
from collections import defaultdict
from collections import Counter
import dataset

# are there null values in any of the tables today?

today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
subject = "[treasury.io tests] distinct_tests.py | %s" % today

# gmail helper
db = dataset.connect("sqlite:///../data/treasury_data.db")

def query(sql):
    res = db.query(sql)
    return [r for r in res]


def gen_queries(params):
    sql_pattern = "SELECT DISTINCT(%s) as %s FROM %s"

    queries = defaultdict(list)
    for t, param in params.iteritems():
        for f in param['fields']:
            queries[t].append({
                'table': t,
                'field': f,
                'query': sql_pattern % (f, f, t)
                })
    return queries

def parse_output(q, o):
    output = defaultdict(list)
    output["table"] = q["table"]
    output["field"] = q["field"]
    for i in o:
        output["values"].append(i[f])
    return output

def test_data(output, distinct_fields):
    msgs = []
    for o in output:
        d = [d for d in distinct_fields if d['table'] == o['table'] and d['field'] == o['field']][0]
        expected = Counter(d['values'])
        found = Counter(o['values'])
        new_values = list((found - expected).elements())
        if len(new_values) > 0:
            msg = """
            <p> <strong> There are %d new values for <em>%s</em> in <em>%s</em>: </strong> </p> %s
            """  % (len(new_values), d['field'], d['table'], "<br></br>".join(new_values))

            msgs.append(msg)
    if len(msgs)==0:
        return "There are no new values in the database today."
    else:
        return "<br></br>".join(msgs)  

@email   
def distinct_tests():
    print "\nINFO: Testing for new values in the dataset\n"
    # setup
    params = json.load(open('distinct_test_params.json'))
    distinct_fields = json.load(open('distinct_fields.json'))
    queries = gen_queries(params)
    output = []
    for t, qs in queries.iteritems():
        for q in qs:
            oo = query(q['query'])
            o_dict = {
            "table": q['table'],
            "field": q['field'],
            "values": sorted([o.values()[0] for o in oo if o.values()[0]])
            }
            output.append(o_dict)
    msg = test_data(output, distinct_fields)
    salutation = """ 
             <p>Hello,</p> 
             """
    postscript = """
                <p> The parameters for these tests can be set in: </p>  
                <p> https://github.com/csvsoundsystem/federal-treasury-api/blob/master/tests/distinct_fields.json </p> 
                <p> https://github.com/csvsoundsystem/federal-treasury-api/blob/master/tests/distinct_tests_params.json </p>
                <p> xoxo, </p>
                <p> \t treasury.io</p>
                """ 
    print msg
    return  subject, salutation + "<p>" + msg + "</p>" + postscript

if __name__ == '__main__':
    try:
       distinct_tests()
    except TypeError:
        pass
