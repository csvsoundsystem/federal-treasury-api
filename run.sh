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
echo All of the fixies have been downloaded and parsed.
echo
echo Everything that the script created is in the data directory.
echo The raw files are in data/fixie. They were parsed and converted
echo to CSVs in the data/daily_csv directory. These are combined by
echo table in the data/lifetime_csv directory.
echo

# Tweet if running on ScraperWiki
if uname -n|grep scraperwiki; then
  echo Tweeting
  python ~/twitter/tweetbot.py
fi
