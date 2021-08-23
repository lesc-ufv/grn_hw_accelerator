#!/bin/bash

my_dir=$(pwd)
rm -rf report.csv
touch report.csv
flag=0
for p in $(find . -iname "prj_name" | grep "sw/host")
do
   cd $my_dir/$(dirname $p)
   cd ../lib
   make
   cd ../host
   cp $my_dir/../awsxclbin/$(cat prj_name).awsxclbin ../../hw/synthesis
   N=$(cat include/acc_config.h | grep "NUM_NOS " | awk '{split($3,a,")");split(a[1],b,"(");print b[2]}')
   C=$(cat include/acc_config.h | grep "NUM_COPIES " | awk '{split($3,a,")");split(a[1],b,"(");print b[2]}')
   python3 $my_dir/../misc/generate_grn_input.py -s "2**20" -n $N -c $C -o grn_input_file.csv
   make $1
   if [ $flag -eq 0 ]
   then
	cat performance_report.csv >> $my_dir/report.csv
	flag="1"
   else
    tail -n 1 performance_report.csv >> $my_dir/report.csv
   fi
   cd ..
   cd $my_dir
   echo "=================================================================================================="
   echo ""
done
