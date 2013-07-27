#!/bin/bash
set -e

if [ -d env ]; then
  . ./env/bin/activate
  echo Activated virtualenv
fi

git checkout master
git pull origin master

# tweet
cd ./twitter
python tweetbot.py -t $1
