#!bin/bash
#!bin/bash
(
  cd ./tests
  python is_it_running.py
  python null_tests.py
  python distinct_fields.py
  cd ..
)
