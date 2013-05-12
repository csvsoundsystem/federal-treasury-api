#!/usr/bin/env python2
# Derived from scraperwiki/dumptruck-web, MIT license

import os
import json
import sqlite3

import dumptruck
from bottle import route, run, response, static_file

class QueryError(Exception):
    """Exception during query processing."""
    def __init__(self, msg, code, **k):
        """Code which catches these exceptions, expects to find an HTTP Status code in
        code.
        """
        self.code = code
        super(QueryError, self).__init__(msg, **k)

def _authorizer_readonly(action_code, tname, cname, sql_location, trigger):
    """SQLite callback that we use to prohibit any SQL commands that could change a
    database; effectively making it readonly.

    Copied from scraperwiki.com sources.
    """

    readonlyops = [
        sqlite3.SQLITE_SELECT,
        sqlite3.SQLITE_READ,
        sqlite3.SQLITE_DETACH,

        # 31=SQLITE_FUNCTION missing from library.
        # codes: http://www.sqlite.org/c3ref/c_alter_table.html
        31,
    ]
    if action_code in readonlyops:
        return sqlite3.SQLITE_OK

    if action_code == sqlite3.SQLITE_PRAGMA:
        tnames_ok = {
            "table_info",
            "index_list",
            "index_info",
            "page_size",
            "synchronous"
        }
        if tname in tnames_ok:
            return sqlite3.SQLITE_OK

    # SQLite FTS (full text search) requires this permission even when reading,
    # and this doesn't let ordinary queries alter sqlite_master because of
    # PRAGMA writable_schema
    if action_code == sqlite3.SQLITE_UPDATE and tname == "sqlite_master":
        return sqlite3.SQLITE_OK

    return sqlite3.SQLITE_DENY

class NotOK(Exception):
    """Some problem meaning we immediately want to return a
    status code that is not 200."""
    def __init__(self, code, body):
        self.code = code
        self.body = body

def open_dumptruck(dbname):
    """Returns read-only dumptruck object, or raises an Exception.
    """
    if os.path.isfile(dbname):
        # Check for the database file
        try:
            dt = dumptruck.DumpTruck(dbname, adapt_and_convert = False)
        except sqlite3.OperationalError, e:
            if e.message == 'unable to open database file':
                msg = e.message + ' (Check that the file exists and is readable by everyone.)'
                code = 500
                raise NotOK(code, msg)
    else:
        msg = 'Error: database file does not exist.'
        code = 500
        raise NotOK(code, msg)

    dt.connection.set_authorizer(_authorizer_readonly)
    return dt

def execute_query(sql, dbname):
    """
    Given an SQL query and a SQLite database name, return an HTTP status code
    and the JSON-encoded response from the database.
    """
    try:
        dt = open_dumptruck(dbname)
    except NotOK as e:
        return e.code, e.body

    try:
        data = dt.execute(sql)
        code = 200
    except sqlite3.OperationalError, e:
        data = u'SQL error: ' + e.message
        code = 400
    except sqlite3.DatabaseError, e:
        data = u'Database error: ' + e.message
        if e.message == u"not authorized":
            # Writes are not authorized.
            code = 403
        else:
            code = 500
    except Exception, e:
        data = u'Error: ' + e.message
        code = 500

    return code, data


@route('/')
def index():
    return 'GET /sql/SELECT+*+FROM+t1;'

@route('/sql/:sql')
def sql(sql='SELECT * FROM sqlite_master;'):
    dbname=os.path.join('data', 'fms.db')
    try:
        code,body = execute_query(sql, dbname)
    except QueryError as e:
        code = e.code
        body = e.message

    response.status = code
    response.set_header('Content-Language', 'en')
    response.set_header('Content-Type', 'application/json; charset=utf-8')
    body = json.dumps(body,sort_keys=True,indent=2)
    return body

@route('/csv/<filename>')
def server_static(filename):
    return static_file(filename, root=os.path.join('data', 'lifetime_csv'))

# run(host='localhost', port=8080)

# Allow any host
run(host='0.0.0.0',port=8080)
