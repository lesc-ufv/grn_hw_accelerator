import math

from veriloggen import *

from fpga_gen.src.hw.grn_aws import GrnAws
from fpga_gen.src.hw.utils import readFile, initialize_regs


class GrnAccelerator:
    def __init__(self, num_networks, grn_arch_file):
        # constants

        self.grn_copies_per_network = 32
        self.grn_fifo_in_size = 2 ** 3
        self.grn_fifo_out_size = 2 ** 3
        self.grn_atractor_width = 32
        self.grn_transient_width = 32
        self.grn_id_width = 32

        # needed variables
        self.acc_num_networks = num_networks
        self.grn_arch_file = grn_arch_file
        self.acc_num_in = math.ceil(num_networks / self.grn_copies_per_network)
        self.acc_num_out = self.acc_num_in
        self.grn_functions = readFile(grn_arch_file)
        self.grn_num_nos = len(self.grn_functions)

        self.acc_data_in_width = self.grn_id_width + math.ceil(
            self.grn_num_nos / 8) * 8 * 2  #grn_id_width + start_state_width(aligned 8b) + end_state_width(aligned 8b)

        self.acc_data_out_width = self.grn_id_width + self.grn_transient_width + self.grn_atractor_width +  self.grn_num_nos

        self.axi_bus_data_width =  int(math.pow(2,math.ceil(math.log2(max(self.acc_data_out_width,self.acc_data_in_width)))))


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
        acc_user_read_data = m.Input('acc_user_read_data', self.axi_bus_data_width * self.acc_num_in)

        acc_user_available_write = m.Input('acc_user_available_write', self.acc_num_out)
        acc_user_request_write = m.Output('acc_user_request_write', self.acc_num_out)
        acc_user_write_data = m.Output('acc_user_write_data', self.axi_bus_data_width * self.acc_num_out)

        acc_user_done = m.Output('acc_user_done')

        start_reg = m.Reg('start_reg')
        grn_done = m.Wire('grn_done', self.get_num_in())

        acc_user_done.assign(Uand(grn_done))

        m.Always(Posedge(clk))(
          If(rst)(
             start_reg(Int(0,1,2))
          ).Else(
             start_reg(Or(start_reg, start))
          )
        )

        num_redes = self.acc_num_networks
        for i in range(self.get_num_in()):
            if num_redes >= self.grn_copies_per_network:
                copies = self.grn_copies_per_network
            else:
                copies = num_redes
            grn = grn_aws.get(copies, self.grn_functions, self.grn_fifo_in_size, self.grn_fifo_out_size,
                              self.acc_data_in_width, self.acc_data_out_width, self.grn_transient_width,
                              self.grn_atractor_width, self.grn_id_width)

            in_init =  i * self.axi_bus_data_width
            in_end = ((i * self.axi_bus_data_width) + 1) + self.acc_data_in_width

            out_init =  i * self.axi_bus_data_width
            out_end = ((i * self.axi_bus_data_width) + 1) + self.acc_data_out_width

            par = []
            con = [('clk', clk), ('rst', rst), ('start', start_reg), ('grn_done_rd_data', acc_user_done_rd_data[i]),
                   ('grn_done_wr_data', acc_user_done_wr_data[i]), ('grn_request_read', acc_user_request_read[i]),
                   ('grn_read_data_valid', acc_user_read_data_valid[i]),
                   ('grn_read_data', acc_user_read_data[in_init:in_end-1]),
                   ('grn_available_write', acc_user_available_write[i]),
                   ('grn_request_write', acc_user_request_write[i]),
                   ('grn_write_data', acc_user_write_data[out_init:out_end-1]),
                   ('grn_done', grn_done[i])]
            m.Instance(grn, '%s_%d' % (grn.name, i), par, con)
            num_redes = num_redes - self.grn_copies_per_network

        initialize_regs(m)

        return m


