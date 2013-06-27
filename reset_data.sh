#!/bin/bash
rm -r data/daily_csv/
rm -r data/lifetime_csv/
rm data/fms.db
cd code
python download_and_parse_fms_fixies.py
