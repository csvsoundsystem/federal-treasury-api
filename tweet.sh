#!/bin/bash
set -e

if [ -d env ]; then
  . ./env/bin/activate
  echo Activated virtualenv
fi

cd ./twitter
python tweetbot.py -t $1
