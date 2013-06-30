
crontab -l > /tmp/crontab
utils/crontab.sh > /tmp/crontab
cat /tmp/crontab | crontab
rm /tmp/crontab
