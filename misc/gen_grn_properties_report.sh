#!/bin/bash

my_dir=$(pwd)
rm -rf grn_properties_report.csv
touch grn_properties_report.csv
flag=0
for p in $(find $1 -iname "*.txt")
do
    python3 extract_grn_properties.py -g $p >> grn_properties_report.csv

done
