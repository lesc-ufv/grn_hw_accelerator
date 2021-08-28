#!/bin/bash

grn_file=$1
out_dir=$2

mkdir $out_dir
cp ./resources/template/Makefile ./resources/template/main.cu ./resources/template/timer.h $out_dir
python3 ./src/grn_gpu_generator.py $grn_file $out_dir
