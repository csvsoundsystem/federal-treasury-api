#!/bin/sh
set -e 

if [ -d env ]; then
  . ./env/bin/activate
  echo Activated virtualenv
fi

git checkout gh-pages
git pull origin gh-pages
cd code
./download_and_parse_fms_fixies.py
echo Downloaded and parsed fixies
