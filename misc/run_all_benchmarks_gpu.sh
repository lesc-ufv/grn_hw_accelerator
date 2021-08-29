#!/bin/bash

SIZE="2**10"
SM=sm_30
my_dir=$(pwd)
rm -rf report.csv
echo "Name,Execution time(ms)" >> report.csv
flag=0
for p in $(find . -iname "main.cu")
do
   cd $my_dir/$(dirname $p)
   make SM=$SM &> /dev/null
   N=$(cat grn_gpu.h | grep "NUM_NOS " | awk '{split($3,a,")");split(a[1],b,"(");print b[2]}')
   python3 $my_dir/../misc/generate_grn_input.py -s $SIZE -n $N -c $SIZE -o grn_input_file.csv
   ./main.exe grn_input_file.csv grn_output_file.csv
   name=$(basename $(pwd))
   time=$(tail -n 1 performance_report.csv)
   echo "$name,$time" >> $my_dir/report.csv
   cd ..
   cd $my_dir
   echo "=================================================================================================="
   echo ""
done
