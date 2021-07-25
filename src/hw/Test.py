from make_gnr_harp import create_gnr_harp
from utils import readFile

path = '../../benchmarks/Benchmark_188.txt'

functions = readFile(path)

create_gnr_harp(32, functions, 2 ** 3, 2 ** 12).to_verilog('Samples/gnr_rtl_188')
