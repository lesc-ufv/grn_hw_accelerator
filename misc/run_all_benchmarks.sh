#!/bin/bash

my_dir=$(pwd)
rm -rf report.csv
touch report.csv

for p in $(find . -iname "prj_name" | grep "sw/host")
do
   cd $my_dir/$(dirname $p)
   cd ../lib
   make
   cd ../host
   N=$(cat include/acc_config.h | grep "NUM_NOS " | awk '{split($3,a,")");split(a[1],b,"(");print b[2]}')
   C=$(cat include/acc_config.h | grep "NUM_COPIES " | awk '{split($3,a,")");split(a[1],b,"(");print b[2]}')
   echo $N
   echo $C
   python3 $my_dir/../misc/generate_grn_input.py -s "2**28" -n $N -c $C -o grn_input_file.csv
   make $1
   cd ..
   cd $my_dir
done
