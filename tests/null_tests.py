#!/usr/bin/env python
# Tested by Tom on Python 2.7.5 and Python 3.3.1 running on Arch Linux
import json
import datetime
from requests import get
from postmark import email
from collections import defaultdict
# null tests
# are there null values in any of the tables today?

today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
subject = "[treasury.io tests] null_tests.py | %s" % today

def query(sql):
    url = 'https://premium.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql'
    r = get(url, params = {'q': sql})
    return r.json()

def gen_queries(params):
    sql_pattern = "SELECT %s FROM %s WHERE %s IS NULL"

    queries = defaultdict(list)
    for t, param in params.iteritems():
        for f in param['fields']:
            for v in param['values']:
                queries[t].append({
                    'table': t,
                    'field': f,
                    'ignore': param['ignore'] if param.has_key("ignore") else [],
                    'value': v,
                    'query': sql_pattern % (f, t, v)
                })
    return queries

def parse_query_results(q, results):
    if len(q['ignore']) > 0:
        for i in q['ignore']:
            if q['field']==i.keys()[0]:
                print "IGNORING: %s" % i.values()[0]
                return [ r[q['field']] for r in results if r[q['field']]!=i.values()[0]]
    else:
        return [r[q['field']] for r in results if r[q['field']] is not None]

def format_err_msg(q, results):
    null_strings = "\n".join(results)
    if null_strings is not None and len(results)>0:
        return """
            <p> These are the current values of %s in <em>%s</em> where %s is NULL:</p>
            <p>%s</p> 
            """ % (q['field'], q['table'], q['value'], null_strings)
    else:
        return ""

def gen_msgs(msgs):
        # generate emails
    

    if len(msgs)>0:
        salutation = """ 
                     <p>Hello,</p> 
                     <p>here are all the null values in the treasury.io database at 
                        <em>%s</em>:
                     </p>
                     """ % today

        postscript = """
                    <p> The parameters for these tests can be set in: \r\n 
                    https://github.com/csvsoundsystem/federal-treasury-api/blob/master/tests/null_test_params.json
                    </p> 
                     <p> xoxo, </p>
                     <p> \t treasury.io</p>
                     """ 

        msg =  salutation + "<br></br>".join(msgs) + postscript
        print "\nEMAIL: %s" % msg
        return "ERROR: " + subject, msg

    else:
        msg =  """
                <p>Hello,</p> 
                <p> There are no relevant null values in the treasury.io database at <em>%s</em></p>
                <p> The parameters for these tests can be set in: \r\n 
                https://github.com/csvsoundsystem/federal-treasury-api/blob/master/tests/null_test_params.json
                </p> 
                <p> xoxo, </p>
                <p> \t treasury.io</p>
                """ % today
        print "\nEMAIL: %s" % msg
        return subject, msg

@email
def null_tests():
    print "\nINFO: Testing for null values in the dataset\n"
    # setup
    params = json.load(open('null_test_params.json'))
    queries = gen_queries(params)
    # generate error messages
    msg_list = []
    for t, qs in queries.iteritems():
        for q in qs:
            print "QUERY: %s" % q['query']
            results = query(q['query'])
            parsed_results = parse_query_results(q, results)
            msg_list.append(format_err_msg(q, parsed_results))

    # filter generated messages
    filtered_msgs = [m for m in msg_list if m is not None and m is not ""]

    return gen_msgs(filtered_msgs)

if __name__ == '__main__':
    try:
        null_tests()
    except TypeError:
        pass
