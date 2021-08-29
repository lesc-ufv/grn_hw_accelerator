#!/bin/bash

if echo "$SHELL" | grep 'bash' >/dev/null 2>&1 ; then
  MYPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
else
  MYPATH="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"
fi

grn_file=$1
out_dir=$2

temp_files="$MYPATH/resources/template/"

mkdir -p $out_dir
cp $temp_files/Makefile $temp_files/main.cu $temp_files/timer.h $out_dir
python3 $MYPATH/src/grn_gpu_generator.py $grn_file $out_dir
