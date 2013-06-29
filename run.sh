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
  cd code
  python download_and_parse_fms_fixies.py
)
echo Downloaded and parsed fixies

# Tweet if running on ScraperWiki
if uname -n|grep scraperwiki; then
  echo Tweeting
  python ~/twitter/tweetbot.py
fi
