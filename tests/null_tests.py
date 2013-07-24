#!/usr/bin/env python
# Tested by Tom on Python 2.7.5 and Python 3.3.1 running on Arch Linux
import json
import datetime
from requests import get
from postmark import email
from collections import defaultdict
# null tests
# are there null values in any of the tables today?

def query(sql):
    url = 'https://premium.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql'
    r = get(url, params = {'q': sql})
    return r.json()

def gen_queries(params):
    sql_pattern = "SELECT \'%s\' FROM \'%s\' WHERE \'%s\' IS NULL"

    queries = defaultdict(list)
    for t, param in params.iteritems():
        for f in param['fields']:
            for v in param['values']:
                queries[t].append({
                    'table': t,
                    'field': f,
                    'value': v,
                    'query': sql_pattern % (f, t, v)
                })
    return queries

def format_err_msg(q, results):
    results = [r for r in results if r is not None]
    null_strings = "\n".join(results)
    if null_strings is not None and len(results)>0:
        return """
            <p> These are the current values of %s in <em>%s</em> where %s is NULL:</p>
            <p>%s</p> 
            """ % (q['field'], q['table'], q['value'], null_strings)
    else:
        return ""
@email
def null_tests():
    print "\nINFO: Testing for null values in the dataset\n"
    # setup
    params = json.load(open('null_test_params.json'))
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = "[treasury.io tests] null_tests.py | %s" % today

    queries = gen_queries(params)
    # generate error messages
    msg_list = []
    for t, qs in queries.iteritems():
        for q in qs:
            print "QUERY: %s" % q['query']
            results = query(q['query'])
            msg_list.append(format_err_msg(q, results))

    # filter generated messages
    filtered_msgs = [m for m in msg_list if m is not None and m is not ""]

    # generate emails
    if len(filtered_msgs)>0:
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

        msq =  salutation + "<br></br>".join(filtered_msgs) + postscript
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

            

if __name__ == '__main__':
    try:
        null_tests()
    except TypeError:
        pass
