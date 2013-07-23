#!/usr/bin/env python
# Tested by Tom on Python 2.7.5 and Python 3.3.1 running on Arch Linux
import json
import datetime
from requests import get
from gmail import gmail
from collections import defaultdict
# null tests
# are there null values in any of the tables today?



def query(sql):
    url = 'https://premium.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql'
    r = get(url, params = {'q': sql})
    return r.json()

def gen_queries(params):
    sql_pattern = "SELECT \'%s\' FROM \'%s\' WHERE date = (SELECT MAX(date) FROM \'%s\') AND \'%s\' IS NULL"

    queries = defaultdict(list)
    for t, param in params.iteritems():
        for f in param['fields']:
            for v in param['values']:
                queries[t].append({
                    'table': t,
                    'field': f,
                    'value': v,
                    'query': sql_pattern % (f, t, t, v)
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
@gmail
def null_tests():
    # setup
    params = json.load(open('null_test_params.json'))
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                     <p> xoxo, </p>
                     <p> \t treasury.io/</p>
                     """ 

        return salutation + "<br></br>".join(filtered_msgs) + postscript

    else:
        return   """
                <p>Hello,</p> 
                <p> There are no <u>relevant</u> null values in the treasury.io database at <em>%s</em></p> 
                <p> xoxo, </p>
                <p> \t treasury.io/</p>
                """ % today

            

if __name__ == '__main__':
  try:
      null_tests()
  except TypeError:
      pass