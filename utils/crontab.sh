#!/bin/sh
MAILTO="csvsoundsystem@gmail.com"
echo "0 17 * * * cd '$PWD' && git pull && ./run.sh"
echo "52 14 * * * cd '$PWD' && /usr/bin/python twitter/tweetbot.y -t is_it_running"
