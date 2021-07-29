import math

from veriloggen import *

from fpga_gen.src.hw.grn_aws import GrnAws
from fpga_gen.src.hw.utils import readFile


class GrnAccelerator:
    def __init__(self, num_networks, grn_arch_file):
        # constants
        self.axi_bus_data_width = 512
        self.grn_copies_per_network = 8
        self.grn_fifo_in_size = 2 ** 3
        self.grn_fifo_out_size = 2 ** 3
        self.grn_atractor_width = 32
        self.grn_transient_width = 32
        self.grn_id_width = 16

        # needed variables
        self.acc_num_networks = num_networks
        self.grn_arch_file = grn_arch_file
        self.acc_num_in = math.ceil(num_networks / self.grn_copies_per_network)
        self.acc_num_out = self.acc_num_in
        self.grn_functions = readFile(grn_arch_file)
        self.grn_num_nos = len(self.grn_functions)
        # comentário Legado...  soma 58  sendo 29 para periodo e 29 para transiente

        self.acc_data_in_width = self.grn_id_width + math.ceil(
            self.grn_num_nos / 8) * 8 * 2  # grn_id_width + start_state_width(aligned 8b) + end_state_width(aligned 8b)
        self.acc_data_out_width = self.grn_id_width + self.grn_transient_width + self.grn_atractor_width + math.ceil(
            self.grn_num_nos / 8) * 8

    def get_num_in(self):
        return self.acc_num_in

    def get_num_out(self):
        return self.acc_num_out

    def get(self):
        return self.__create_grn_accelerator()

    def __create_grn_accelerator(self):
        grn_aws = GrnAws()

        m = Module('grn_acc')
        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')
        acc_user_done_rd_data = m.Input('acc_user_done_rd_data', self.acc_num_in)
        acc_user_done_wr_data = m.Input('acc_user_done_wr_data', self.acc_num_out)

        acc_user_request_read = m.Output('acc_user_request_read', self.acc_num_in)
        acc_user_read_data_valid = m.Input('acc_user_read_data_valid', self.acc_num_in)
        acc_user_read_data = m.Input('acc_user_read_data', self.acc_data_in_width * self.acc_num_in)

        acc_user_available_write = m.Input('acc_user_available_write', self.acc_num_out)
        acc_user_request_write = m.Output('acc_user_request_write', self.acc_num_out)
        acc_user_write_data = m.Output('acc_user_write_data', self.acc_data_out_width * self.acc_num_out)

        acc_user_done = m.Output('acc_user_done')
        grn_done = m.Wire('grn_done', self.get_num_in())
        acc_user_done.assign(Uand(grn_done))

        num_redes = self.acc_num_networks
        for i in range(self.get_num_in()):
            if num_redes >= self.grn_copies_per_network:
                copies = self.grn_copies_per_network
            else:
                copies = num_redes
            grn = grn_aws.get(copies, self.grn_functions, self.grn_fifo_in_size, self.grn_fifo_out_size,
                              self.acc_data_in_width, self.acc_data_out_width, self.grn_transient_width,
                              self.grn_atractor_width, self.grn_id_width)
            par = []
            con = [('clk', clk), ('rst', rst), ('start', start), ('grn_done_rd_data', acc_user_done_rd_data[i]),
                   ('grn_done_wr_data', acc_user_done_wr_data[i]), ('grn_request_read', acc_user_request_read[i]),
                   ('grn_read_data_valid', acc_user_read_data_valid[i]),
                   ('grn_read_data', acc_user_read_data[self.acc_data_in_width * i:(i + 1) * self.acc_data_in_width]),
                   ('grn_available_write', acc_user_available_write[i]),
                   ('grn_request_write', acc_user_request_write[i]),
                   ('grn_write_data', acc_user_write_data[self.acc_data_out_width * i:(i + 1) * self.acc_data_out_width]),
                   ('grn_done', grn_done[i])]
            m.Instance(grn, '%s_%d' % (grn.name, i), par, con)
            num_redes = num_redes - self.grn_copies_per_network
        return m

path = '../../../benchmarks/Benchmark_5.txt'

acc = GrnAccelerator(9, path)
acc.get().to_verilog('./Benchmark_5.v')
