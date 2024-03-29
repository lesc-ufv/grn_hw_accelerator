from veriloggen import *

from fpga_gen.src.hw.grn_components import GrnComponents
from fpga_gen.src.hw.utils import initialize_regs


class GrnAws:
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
        return self.__create_grn_aws()

    def __create_grn_aws(self):
        name = 'grn_aws_%d' % self.copies
        if name in self.cache.keys():
            return self.cache[name]

        grn_components = GrnComponents()

        m = Module(name)

        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')

        grn_done_rd_data = m.Input('grn_done_rd_data')
        grn_done_wr_data = m.Input('grn_done_wr_data')

        grn_request_read = m.Output('grn_request_read')
        grn_read_data_valid = m.Input('grn_read_data_valid')
        grn_read_data = m.Input('grn_read_data', self.data_in_width)

        grn_available_write = m.Input('grn_available_write')
        grn_request_write = m.Output('grn_request_write')
        grn_write_data = m.Output('grn_write_data', self.data_out_width)

        grn_done = m.Output('grn_done')

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

        control_data_in = grn_components.create_control_data_in(self.data_in_width)
        con = [('clk', clk), ('rst', rst), ('start', start), ('grn_read_data_valid', grn_read_data_valid),
               ('grn_read_data', grn_read_data), ('grn_done_rd_data', grn_done_rd_data),
               ('grn_request_read', grn_request_read), ('data_valid', data_in_valid), ('data_out', data_in),
               ('done', control_data_in_done)]
        m.Instance(control_data_in, 'control_data_in', control_data_in.get_params(), con)

        rn = grn_components.create_regulator_network(self.copies, self.functions, self.fifo_in_size, self.fifo_out_size,
                                                     self.id_width, self.data_in_width, self.data_out_width)
        for i in range(self.copies):
            con = [('clk', clk), ('rst', rst), ('start', start),
                   ('data_in_valid', data_in_valid),
                   ('data_in', data_in),
                   ('read_data_en', read_data_en[i]),
                   ('has_data_out', has_data[i]),
                   ('has_lst3_data_out', has_lst3_data[i]),
                   ('data_out', data_out[i]),
                   ('end_data_in',control_data_in_done),
                   ('task_done', task_done[i])]
            m.Instance(rn, 'rn%d' % i, [('ID', i + 1)], con)

        control_data_out = grn_components.create_control_data_out(self.copies, self.data_out_width)
        con = [('clk', clk), ('rst', rst), ('start', start), ('grn_done_wr_data', grn_done_wr_data),
               ('grn_available_write', grn_available_write), ('grn_request_write', grn_request_write),
               ('grn_write_data', grn_write_data),('has_data',has_data),('has_lst3_data',has_lst3_data)]
        for i in range(self.copies):
            con.append(('din%d' % i, data_out[i]))

        con.append(('read_data_en', read_data_en))
        con.append(('task_done', task_done))
        con.append(('done', grn_done))

        m.Instance(control_data_out, 'control_data_out', control_data_out.get_params(), con)

        initialize_regs(m)

        self.cache[name] = m
        return m
