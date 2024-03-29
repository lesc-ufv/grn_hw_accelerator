from fpga_gen.src.hw.grn_components import GrnComponents
from fpga_gen.src.hw.utils import readFile

path = '../../benchmarks/Benchmark_5.txt'
functions = readFile(path)
gnr_components = GrnComponents()
gnr_components.create_gnr_harp(10, functions, 2 ** 3, 2 ** 12).to_verilog('../../Samples/gnr_rtl_5/Benchmark_5.v')
