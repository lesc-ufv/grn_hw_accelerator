import math

from veriloggen import *

from src.hw.gnr_aws import GnrAws
from src.hw.gnr_components import GnrComponents
from src.hw.utils import readFile


class GnrAccelerator:
    def __init__(self, num_redes, gnr_arch_file):
        self.gnr_copies = 8
        self.num_redes = num_redes
        self.gnr_arch_file = gnr_arch_file
        self.num_in = math.ceil(num_redes / self.gnr_copies)
        self.num_out = self.num_in
        self.functions = readFile(gnr_arch_file)

    def get_num_in(self):
        return self.num_in

    def get_num_out(self):
        return self.num_out

    def get(self):
        return self.create_gnr_accelerator()

    def create_gnr_accelerator(self):
        gnr_components = GnrComponents()

        m = Module('gnr_acc')
        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')
        acc_user_done_rd_data = m.Input('acc_user_done_rd_data', self.num_in)
        acc_user_done_wr_data = m.Input('acc_user_done_wr_data', self.num_out)

        acc_user_request_read = m.Output('acc_user_request_read', self.num_in)
        acc_user_read_data_valid = m.Input('acc_user_read_data_valid', self.num_in)
        acc_user_read_data = m.Input('acc_user_read_data', 512 * self.num_in)

        acc_user_available_write = m.Input('acc_user_available_write', self.num_out)
        acc_user_request_write = m.Output('acc_user_request_write', self.num_out)
        acc_user_write_data = m.Output('acc_user_write_data', 512 * self.num_out)

        acc_user_done = m.Output('acc_user_done')

        gnr_done = m.Wire('gnr_done', self.get_num_in())

        gnr_aws = GnrAws()
        num_redes = self.num_redes
        cache = {}
        for i in range(self.get_num_in()):
            if num_redes >= self.gnr_copies:
                copies = self.gnr_copies
            else:
                copies = num_redes
            gnr = gnr_aws.get(copies, self.functions, 2 ** 3, 2 ** 3)
            par = []
            con = [('clk', clk), ('rst', rst), ('start', start), ('acc_user_done_rd_data', acc_user_done_rd_data[i]),
                   ('acc_user_done_wr_data', acc_user_done_wr_data[i]),
                   ('acc_user_request_read', acc_user_request_read[i]),
                   ('acc_user_read_data_valid', acc_user_read_data_valid[i]),
                   ('acc_user_read_data', acc_user_read_data[512 * i:(i + 1) * 512]),
                   ('acc_user_available_write', acc_user_available_write[i]),
                   ('acc_user_request_write', acc_user_request_write[i]),
                   ('acc_user_write_data', acc_user_write_data[512 * i:(i + 1) * 512]), ('acc_user_done', gnr_done[i])]
            m.Instance(gnr, '%s_%d' % (gnr.name, i), par, con)
            num_redes = num_redes - self.gnr_copies

        #acc_user_done.assign(m.EmbeddedCode("&gnr_done"))
        return m


path = '../../benchmarks/Benchmark_5.txt'

acc = GnrAccelerator(33, path)
print(acc.create_gnr_accelerator().to_verilog())
