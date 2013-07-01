#!/bin/bash
set -e

if [ -d env ]; then
  . ./env/bin/activate
fi

tmp=$(mktemp)

# Email on error
"$@" &> $tmp || smtpcli -s 'treasury.io error' -t csv@treasury.io -f $tmp --no-confirm

rm $tmp
