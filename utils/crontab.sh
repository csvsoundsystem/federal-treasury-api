#!bin/bash
MAILTO="csvsoundsystem+treasuryiocrontab@gmail.com"
30 20 * * * cd /home && sh run.sh >> logs/run_log 2>> logs/run_err_log
*  17 * * 1,4  cd /home && sh tweet.sh change_in_balance  >> logs/twt_log 2>> logs/twt_err_log
15 20 * * 2,5  cd /home && sh tweet.sh total_debt >> logs/twt_log 2>> logs/twt_err_log
45 00,02,13,17 * * * cd /home && sh tweet.sh random_item >> logs/twt_log 2>> logs/twt_err_log
30 11,15,22 * * * cd /home && sh tweet.sh random_comparison >> logs/twt_log 2>> logs/twt_err_log
01 08 * * * cd /home && sh utils/reset_data.sh >> logs/run_log 2>> logs/run_err_log
