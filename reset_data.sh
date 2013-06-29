#!/bin/bash
set -e

if [ -d env ]; then
  . ./env/bin/activate
  echo Activated virtualenv
fi

git checkout master
git pull origin master

rm -r data/daily_csv/
rm -r data/lifetime_csv/
rm data/fms.db

cd code
./download_and_parse_fms_fixies.py
