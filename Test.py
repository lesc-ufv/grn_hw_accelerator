from make_gnr_harp import make_gnr_harp
from readFile import readFile

path = 'benchmarks/Benchmark_188.txt'

functions = readFile(path)

make_gnr_harp(32, functions, 2 ** 3, 2 ** 12).to_verilog('Samples/gnr_rtl_188')
