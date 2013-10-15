#!bin/bash
(
  cd ./parser
  python download_and_parse_fms_fixies.py
  cd ..
)
./test.sh