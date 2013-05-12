#!/bin/bash
wget https://dl.dropboxusercontent.com/u/6535582/fms_parser_data.zip
unzip fms_parser_data.zip
rm fms_parser_data.zip*
echo 'Commit changes outside of `data`, then run this.'
echo 'git reset --hard'
