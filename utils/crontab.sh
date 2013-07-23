30 20 * * * cd /home && sh run.sh
*  17 * * 1,4  cd /home && sh tweet.sh change_in_balance
15 20 * * 2,5  cd /home && sh tweet.sh total_debt
45 00,02,13,17 * * * cd /home && sh tweet.sh random_item
30 11,15,22 * * * cd /home && sh tweet.sh random_comparison
01 8 * * * cd /home/utils/ && sh reset_data.sh
30 16 * * * cd /home/tests/ && python null_tests.py && python is_it_running.py

