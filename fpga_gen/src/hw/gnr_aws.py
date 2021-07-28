import math
from veriloggen import *


class GnrAws:
    def __init__(self):
        self.cache = {}

    def get(self, num_units, functions, fifo_in_size, fifo_out_size):
        self.num_units = num_units
        self.functions = functions
        self.fifo_in_size = fifo_in_size
        self.fifo_out_size = fifo_out_size
        self.ext_data_width = 512

        self.qtd_nos = len(self.functions)
        self.data_width = self.qtd_nos + 58  # soma 58  sendo 29 para periodo e 29 para transiente
        self.data_width_con = self.data_width
        while self.ext_data_width % self.data_width != 0: self.data_width += 1

        if self.data_width > self.ext_data_width:
            raise Exception('Número máximo de nós ultrapassado!')

        self.data_in_width = int(
            math.ceil(math.log(self.num_units, 2))) + 1 + 2 * self.qtd_nos  # ID + ESTADO INICIAL + ESTADO FINAL
        self.data_in_width_con = self.data_in_width
        while self.ext_data_width % self.data_in_width != 0: self.data_in_width += 1
        if self.data_in_width > self.ext_data_width:
            raise Exception('Número máximo de nós ultrapassado!')
        return self.__create_gnr_aws()

    def __create_gnr_aws(self):
        name = 'gnr_aws_%d' % self.num_units
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')

        acc_user_done_rd_data = m.Input('acc_user_done_rd_data')
        acc_user_done_wr_data = m.Input('acc_user_done_wr_data')

        acc_user_request_read = m.Output('acc_user_request_read')
        acc_user_read_data_valid = m.Input('acc_user_read_data_valid')
        acc_user_read_data = m.Input('acc_user_read_data', self.ext_data_width)

        acc_user_available_write = m.Input('acc_user_available_write')
        acc_user_request_write = m.Output('acc_user_request_write')
        acc_user_write_data = m.Output('acc_user_write_data', self.ext_data_width)

        acc_user_done = m.Output('acc_user_done')

        '''
        num_data_in = m.Wire('num_data_in', 32)
        num_data_out = m.Wire('num_data_out', 32)
        end_data_in = m.Wire('end_data_in')
        task_done = m.Wire('task_done', num_units)
        has_data = m.Wire('has_data', num_units)
        has_lst3_data = m.Wire('has_lst3_data', num_units)
        data_out = []
        for i in range(num_units):
            data_out.append(m.Wire('data_out%d' % i, data_width_con))

        data_in = m.Wire('data_in', data_in_width)
        read_data_en = m.Wire('read_data_en', num_units)
        data_in_valid = m.Wire('data_in_valid')
        num_data_in.assign(afu_context[256:288])
        num_data_out.assign(afu_context[288:320])

        control_data_in = self.create_control_data_in(data_in_width, 512)
        con = [('clk', clk), ('rst', rst), ('start', start), ('num_data_in', num_data_in),
               ('has_data_in', ~fifoin_empty),
               ('has_lst3_data_in', fifoin_almost_empty), ('data_in', rd_fifoin_data), ('rd_request_en', rd_fifoin_en),
               ('data_valid', data_in_valid), ('data_out', data_in), ('done', end_data_in)]
        m.Instance(control_data_in, 'control_data_in', control_data_in.get_params(), con)

        rn = self.create_regulator_network(num_units, functions, fifo_in_size, fifo_out_size)
        for i in range(num_units):
            con = [('clk', clk), ('rst', rst), ('start', start), ('data_in_valid', data_in_valid),
                   ('data_in', data_in[:data_in_width_con]),
                   ('end_data_in', end_data_in),
                   ('read_data_en', read_data_en[i]), ('has_data_out', has_data[i]),
                   ('has_lst3_data_out', has_lst3_data[i]),
                   ('data_out', data_out[i]),
                   ('task_done', task_done[i])]
            m.Instance(rn, 'rn%d' % i, [('ID', i + 1)], con)

        control_data_out = self.create_control_data_out(num_units, data_width)
        con = [('clk', clk), ('rst', rst), ('start', start), ('num_data_out', num_data_out),
               ('fifo_out_full', fifoout_full),
               ('fifo_out_almostfull', fifo_out_almostfull), ('fifo_out_empty', fifoout_empty),
               ('has_data', has_data), ('has_lst3_data', has_lst3_data)]
        for i in range(num_units):
            if data_width - data_width_con > 0:
                con.append(('din%d' % i, Cat(Int(0, data_width - data_width_con, 10), data_out[i])))
            else:
                con.append(('din%d' % i, data_out[i]))

        for pair in [('read_data_en', read_data_en), ('task_done', task_done), ('wr_fifo_out_en', wr_fifoout_en),
                     ('wr_fifo_out_data', wr_fifoout_data), ('done', done)]:
            con.append(pair)

        m.Instance(control_data_out, 'control_data_out', control_data_out.get_params(), con)

        simulation.setup_waveform(m, 'gnr_harp')

        initialize_regs(m)
        self.cache[name] = m
        '''
        self.cache[name] = m
        return m
