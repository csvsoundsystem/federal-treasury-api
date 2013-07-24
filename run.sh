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
echo "Waiting for Database to update before rebuilding schema\r\n"
sleep 20
(
  cd ./schema-builder
  node schema-builder.js
  s3cmd put table_schema.json s3://treasury.io/table_schema.json
  s3cmd setacl s3://treasury.io/ --acl-public --recursive
)
echo "\r\nDone"