#!/bin/sh

echo "0 17 * * * cd '$PWD/code' && ./download_and_parse_fms_fixies.py && sqlite3  ../data/fms.db < to_sqlite3.sql"
