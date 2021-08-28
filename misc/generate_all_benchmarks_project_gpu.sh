#!/bin/sh

create_project="../gpu_gen/create_grn_gpu_project.sh"
bench_dir="../benchmarks/wscad_benchmarks/"

mkdir -p samples_gpu
cd samples_gpu

$create_project $bench_dir/Benchmark_21.txt  Benchmark_21
$create_project $bench_dir/Benchmark_70.txt Benchmark_70
$create_project $bench_dir/Benchmark_188.txt Benchmark_188
$create_project $bench_dir/Erb_reception_247.txt ERB_247
$create_project $bench_dir/EGFR_ErbB_Signaling_104.txt EGFR_104
$create_project $bench_dir/B_bronchiseptica_and_T_retortaeformis_coinfectio_53.txt B_bronchiseptica_53
$create_project $bench_dir/macrophave_321.txt  macrophave_321

