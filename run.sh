#!/bin/sh
set -e 

if [ -d env ]; then
  . ./env/bin/activate
  echo Activated virtualenv
fi

cd code
./download_and_parse_fms_fixies.py
echo Downloaded and parsed fixies

sqlite3  ../data/fms.db < to_sqlite3.sql
echo Imported to SQLite3
