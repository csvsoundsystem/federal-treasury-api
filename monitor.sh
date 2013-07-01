#!/bin/bash
set -e

tmp=$(mktemp)

# Email on error
"$@" &> $tmp || smtpcli -s smtpcli -t csv@treasury.io -f $tmp

rm $tmp
