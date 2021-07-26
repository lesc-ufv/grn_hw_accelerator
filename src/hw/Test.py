from src.hw.gnr_components import GnrComponents
from utils import readFile

path = '../../benchmarks/Benchmark_5.txt'

functions = readFile(path)
gnr_components = GnrComponents()
gnr_components.create_gnr_harp(10, functions, 2 ** 3, 2 ** 12).to_verilog('../../Samples/gnr_rtl_5/Benchmark_5.v')


'''
data_in_valid
data_in
data_in_done

data_request


gravar

request_escrita
data_out

wr_ready


getnumin

accel

acc_axi


'''