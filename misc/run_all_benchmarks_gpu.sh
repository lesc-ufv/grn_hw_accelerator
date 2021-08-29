#!/bin/bash

SM=sm_37
my_dir=$(pwd)
rm -rf report.csv
echo "Name,Execution time(ms)" >> report.csv
flag=0
for p in $(find . -iname "main.cu")
do
   cd $my_dir/$(dirname $p)
   name=$(basename $(pwd))
   SIZE=$(cat size.txt)
   N=$(cat grn_gpu.h | grep "NUM_NOS " | awk '{split($3,a,")");split(a[1],b,"(");print b[2]}')
   echo $name
   make SM=$SM &> /dev/null
   python3 $my_dir/../misc/generate_grn_input.py -s $SIZE -n $N -c $SIZE -o grn_input_file.csv
   ./main.exe grn_input_file.csv grn_output_file.csv
   tim=$(tail -n 1 performance_report.csv)
   echo "$name,$tim" >> $my_dir/report.csv
   cd ..
   cd $my_dir
   echo "=================================================================================================="
   echo ""
done
