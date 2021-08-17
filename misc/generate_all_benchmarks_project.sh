#!/bin/sh

create_project="python3 ../fpga_gen/create_project.py"
bench_dir="../benchmarks/wscad_benchmarks/"

mkdir -p samples
cd samples

$create_project -g $bench_dir/Benchmark_21.txt -n Benchmark_21_32_256 -c 256 -o .
$create_project -g $bench_dir/Benchmark_70.txt -n Benchmark_70_32_64 -c 64 -o .
$create_project -g $bench_dir/Benchmark_188.txt -n Benchmark_188_32_64 -c 64 -o .
$create_project -g $bench_dir/macrophave_321.txt -n macrophave_321_32_64 -c 64 -o .
$create_project -g $bench_dir/Erb_reception_247.txt -n Erb_reception_247_32_64 -c 64 -o .
$create_project -g $bench_dir/EGFR_ErbB_Signaling_104.txt -n EGFR_ErbB_Signaling_104_32_64 -c 64 -o .
$create_project -g $bench_dir/B_bronchiseptica_and_T_retortaeformis_coinfectio_53.txt -n B_bronchiseptica_and_T_retortaeformis_coinfectio_53_32_64 -c 64 -o .
$create_project -g $bench_dir/CD4_T_cell_signaling_188.txt -n CD4_T_cell_signaling_188_32_64 -c 64 -o .
