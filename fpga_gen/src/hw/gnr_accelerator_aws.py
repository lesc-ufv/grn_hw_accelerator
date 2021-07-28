import math

from veriloggen import *

from fpga_gen.src.hw.gnr_aws import GnrAws
from fpga_gen.src.hw.utils import readFile


class GnrAccelerator:
<<<<<<< HEAD
    def __init__(self, num_networks, gnr_arch_file):
        # constants
        self.gnr_copies_per_network = 8
        self.gnr_fifo_in_size = 2 ** 3
        self.gnr_fifo_out_size = 2 ** 3
        self.gnr_atractor_width = 32
        self.gnr_transient_width = 32
        self.gnr_id_width = 16

        # needed variables
        self.acc_num_networks = num_networks
=======
    def __init__(self, num_redes, gnr_arch_file):
        self.axi_bus_data_width = 512
        self.gnr_copies = 8
        self.num_redes = num_redes
>>>>>>> 97171914411b4077451e7f7a66d17ad494b1260a
        self.gnr_arch_file = gnr_arch_file
        self.acc_num_in = math.ceil(num_networks / self.gnr_copies_per_network)
        self.acc_num_out = self.acc_num_in
        self.gnr_functions = readFile(gnr_arch_file)
        self.gnr_num_nos = len(self.gnr_functions)
        # comentário Legado...  soma 58  sendo 29 para periodo e 29 para transiente

        self.acc_data_in_width = self.gnr_id_width + math.ceil(
            self.gnr_num_nos / 8) * 8 * 2  # gnr_id_width + start_state_width(aligned 8b) + end_state_width(aligned 8b)
        self.acc_data_out_width = self.gnr_id_width + self.gnr_transient_width + self.gnr_atractor_width + math.ceil(
            self.gnr_num_nos / 8) * 8

    def get_num_in(self):
        return self.acc_num_in

    def get_num_out(self):
        return self.acc_num_out

    def get(self):
        return self.__create_gnr_accelerator()

    def __create_gnr_accelerator(self):
        gnr_aws = GnrAws()

        m = Module('gnr_acc')
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
        gnr_done = m.Wire('gnr_done', self.get_num_in())
        acc_user_done.assign(Uand(gnr_done))

        num_redes = self.acc_num_networks
        for i in range(self.get_num_in()):
            if num_redes >= self.gnr_copies_per_network:
                copies = self.gnr_copies_per_network
            else:
                copies = num_redes
            gnr = gnr_aws.get(copies, self.gnr_functions, self.gnr_fifo_in_size, self.gnr_fifo_out_size,
                              self.acc_data_in_width, self.acc_data_out_width, self.gnr_transient_width,
                              self.gnr_atractor_width, self.gnr_id_width)
            par = []
            con = [('clk', clk), ('rst', rst), ('start', start), ('gnr_done_rd_data', acc_user_done_rd_data[i]),
                   ('gnr_done_wr_data', acc_user_done_wr_data[i]), ('gnr_request_read', acc_user_request_read[i]),
                   ('gnr_read_data_valid', acc_user_read_data_valid[i]),
                   ('gnr_read_data', acc_user_read_data[self.acc_data_in_width * i:(i + 1) * self.acc_data_in_width]),
                   ('gnr_available_write', acc_user_available_write[i]),
                   ('gnr_request_write', acc_user_request_write[i]),
                   ('gnr_write_data', acc_user_write_data[self.acc_data_out_width * i:(i + 1) * self.acc_data_out_width]),
                   ('gnr_done', gnr_done[i])]
            m.Instance(gnr, '%s_%d' % (gnr.name, i), par, con)
            num_redes = num_redes - self.gnr_copies_per_network

<<<<<<< HEAD
        return m


path = '../../../benchmarks/Benchmark_5.txt'

acc = GnrAccelerator(9, path)
print(acc.get().to_verilog('./Benchmark_5.v'))
=======
        acc_user_done.assign(Uand(gnr_done))
        return m
>>>>>>> 97171914411b4077451e7f7a66d17ad494b1260a
