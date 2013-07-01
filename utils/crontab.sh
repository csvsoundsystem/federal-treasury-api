#!/bin/sh
echo "0 17 * * * cd '$PWD' && git pull && ./monitor.sh ./run.sh"
echo "52 14 * * * cd '$PWD' && /usr/bin/python twitter/tweetbot.y -t is_it_running"
