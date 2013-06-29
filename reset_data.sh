#!/bin/bash
set -e

if [ -d env ]; then
  . ./env/bin/activate
  echo Activated virtualenv
fi

git checkout master
git pull origin master

if [ -f data/daily_csv/]; then
  rm -r data/daily_csv/
fi
if [ -f data/lifetime_csv/]; then
  rm -r data/lifetime_csv/
fi
if [ -f data/fms.db]; then
  rm -r data/fms.db
fi

cd code
./download_and_parse_fms_fixies.py
