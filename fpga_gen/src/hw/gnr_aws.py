import math
from veriloggen import *

from fpga_gen.src.hw.gnr_components import GnrComponents


class GnrAws:
    def __init__(self):
        self.cache = {}

    def get(self, copies, functions, fifo_in_size, fifo_out_size, data_in_width, data_out_width, transient_width,
            atractor_width, id_width):
        self.copies = copies
        self.functions = functions
        self.fifo_in_size = fifo_in_size
        self.fifo_out_size = fifo_out_size
        self.data_in_width = data_in_width
        self.data_out_width = data_out_width
        self.transient_width = transient_width
        self.atractor_width = atractor_width
        self.id_width = id_width
        return self.__create_gnr_aws()

    def __create_gnr_aws(self):
        name = 'gnr_aws_%d' % self.copies
        if name in self.cache.keys():
            return self.cache[name]

        gnr_components = GnrComponents()

        m = Module(name)

        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')

        gnr_done_rd_data = m.Input('gnr_done_rd_data')
        gnr_done_wr_data = m.Input('gnr_done_wr_data')

        gnr_request_read = m.Output('gnr_request_read')
        gnr_read_data_valid = m.Input('gnr_read_data_valid')
        gnr_read_data = m.Input('gnr_read_data', self.data_in_width)

        gnr_available_write = m.Input('gnr_available_write')
        gnr_request_write = m.Output('gnr_request_write')
        gnr_write_data = m.Output('gnr_write_data', self.data_out_width)

        gnr_done = m.Output('gnr_done')

        data_in_valid = m.Wire('data_in_valid')
        control_data_in_done = m.Wire('control_data_in_done')

        data_out = []
        for i in range(self.copies):
            data_out.append(m.Wire('data_out%d' % i, self.data_out_width))

        data_in = m.Wire('data_in', self.data_in_width)
        read_data_en = m.Wire('read_data_en', self.copies)
        has_data = m.Wire('has_data', self.copies)
        has_lst3_data = m.Wire('has_lst3_data', self.copies)
        task_done = m.Wire('task_done', self.copies)

        control_data_in = gnr_components.create_control_data_in(self.data_in_width)
        con = [('clk', clk), ('rst', rst), ('start', start), ('gnr_read_data_valid', gnr_read_data_valid),
               ('gnr_read_data', gnr_read_data), ('gnr_done_rd_data', gnr_done_rd_data),
               ('gnr_request_read', gnr_request_read), ('data_valid', data_in_valid), ('data_out', data_in),
               ('done', control_data_in_done)]
        m.Instance(control_data_in, 'control_data_in', control_data_in.get_params(), con)

        rn = gnr_components.create_regulator_network(self.copies, self.functions, self.fifo_in_size, self.fifo_out_size,
                                                     self.id_width, self.data_in_width, self.data_out_width)
        for i in range(self.copies):
            con = [('clk', clk), ('rst', rst), ('start', start), ('data_in_valid', data_in_valid), ('data_in', data_in),
                   ('control_data_in_done', control_data_in_done),
                   ('read_data_en', read_data_en[i]), ('has_data_out', has_data[i]),
                   ('has_lst3_data_out', has_lst3_data[i]),
                   ('data_out', data_out[i]),
                   ('task_done', task_done[i])]
            m.Instance(rn, 'rn%d' % i, [('ID', i + 1)], con)

        control_data_out = gnr_components.create_control_data_out(self.copies, self.data_out_width)
        con = [('clk', clk), ('rst', rst), ('start', start), ('gnr_done_wr_data', gnr_done_wr_data),
               ('gnr_available_write', gnr_available_write), ('gnr_request_write', gnr_request_write),
               ('gnr_write_data', gnr_write_data)]
        for i in range(self.copies):
            con.append(('din%d' % i, data_out[i]))

        con.append(('read_data_en', read_data_en))
        con.append(('task_done', task_done))
        con.append(('done', gnr_done))

        m.Instance(control_data_out, 'control_data_out', control_data_out.get_params(), con)

        simulation.setup_waveform(m, 'gnr_aws')

        # initialize_regs(m)

        self.cache[name] = m
        return m
