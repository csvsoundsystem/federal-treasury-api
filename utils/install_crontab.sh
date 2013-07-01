
crontab -l > /tmp/crontab
./crontab.sh > /tmp/crontab
cat /tmp/crontab | crontab
rm /tmp/crontab
echo "NEW CRONTAB:"
crontab -l
