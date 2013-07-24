#!bin/bash
MAILTO="csvsoundsystem+treasuryiocrontab@gmail.com"
30 20 * * * cd /home && sh run.sh >> logs/run_log 2>> logs/run_err.log
*  17 * * 1,4  cd /home && sh tweet.sh change_in_balance  >> logs/twt_log 2>> logs/twt_err.log
15 20 * * 2,5  cd /home && sh tweet.sh total_debt >> logs/twt_log 2>> logs/twt_err.log
45 00,02,13,17 * * * cd /home && sh tweet.sh random_item >> logs/twt_log 2>> logs/twt_err.log
30 11,15,22 * * * cd /home && sh tweet.sh random_comparison >> logs/twt_log 2>> logs/twt_err.log
01 8 * * * cd /home/utils/ && sh reset_data.sh >> ../logs/run_log 2>> ../logs/run_err.log
30 16 * * * cd /home/tests/ && python null_tests.py && python is_it_running.py  >> ../logs/test.log 2>> ../logs/test_err.log

