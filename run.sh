#!/bin/sh
set -e

if [ -d env ]; then
  . ./env/bin/activate
  echo Activated virtualenv
  pip install --upgrade -r requirements.pip
fi

git checkout master
git pull origin master

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
)
echo "INFO: Building schema_table.json \r\n"
(
  cd ./schema-builder
  node db-schema-builder.js
  echo "INFO: Uploading schema_table.json to s3\r\n"
  s3cmd put table_schema.json s3://treasury.io/db_schema.json
  s3cmd setacl s3://treasury.io/ --acl-public --recursive
  cd ..
)
echo "\r\nDone!\r\n"