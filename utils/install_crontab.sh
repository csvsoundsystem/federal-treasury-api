#!/bin/sh
crontab -l > /tmp/crontab.bak
cat "$HOME/utils/crontab" | crontab
echo "NEW CRONTAB:"
crontab -l
echo "OLD CRONTAB: Backed up to /tmp/crontab.bak"
