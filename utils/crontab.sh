#!/bin/sh
MAILTO="csvsoundsystem@gmail.com"
30 16 * * * cd '$PWD' && git pull && ./monitor.sh ./run.sh
*  17 * * 1,4  /bin/bash /home/tweet.sh change_in_balance
10 15 * * 2,5  /bin/bash /home/tweet.sh total_debt
30 11 * * * /bin/bash /home/tweet.sh is_it_running
45 9,11,13,15,20,22 * * * /bin/bash /home/tweet.sh random_item
