#!/bin/sh
echo "0 17 * * * cd '$PWD' && git pull && ./run.sh"
