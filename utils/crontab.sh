#!/bin/sh
echo "0 17 * * * cd '$PWD' && git pull && ./run.sh"
echo "0 12 * * * cd '$PWD' && /usr/bin/python tests/is_it_running.py --tweet True
