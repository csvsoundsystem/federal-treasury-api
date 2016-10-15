#!/bin/sh
set -e

if [ -d env ]; then
  . ./env/bin/activate
  echo Activated virtualenv
  pip install --upgrade -r requirements.pip
fi

git checkout master
git pull origin master
npm install

(
  cd ./parser
  python download_and_parse_fms_fixies.py
  cd ..
)
echo "INFO: Waiting for Database to update before proceeding\r\n"
sleep 20
echo "INFO: Running tests\r\n"
(
  cd ./tests
  python is_it_running.py
  python null_tests.py
  python distinct_tests.py
  cd ..
)
echo "INFO: Building db_schema.json \r\n"
(
  cd ./schema-builder
  npm run build-schema
)
echo "\r\nDone!\r\n"
