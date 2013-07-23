#!/bin/bash
set -e

if [ -d env ]; then
  . ./env/bin/activate
  echo Activated virtualenv
fi

git checkout master
git pull origin master

(
  cd ../schema-builder
  node schema-builder.js
  s3cmd put table_schema.json s3://treasury.io/table_schema.json
)
