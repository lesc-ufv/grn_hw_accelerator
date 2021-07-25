import math

from veriloggen import *

from create_control_data_in import make_control_data_in
from create_control_data_out import make_control_data_out
from src.hw.gnr_components import Components


def create_gnr_harp(num_units, functions, fifo_in_size, fifo_out_size):
    components = Components()
    qtd_nos = len(functions)
    data_width = qtd_nos + 58  # soma 58  sendo 29 para periodo e 29 para transiente
    data_width_con = data_width
    while 512 % data_width != 0: data_width += 1

    if data_width > 512:
        raise Exception('Número máximo de nós ultrapassado!')

    data_in_width = int(math.ceil(math.log(num_units, 2))) + 1 + 2 * qtd_nos  # ID + ESTADO INICIAL + ESTADO FINAL
    data_in_width_con = data_in_width
    while 512 % data_in_width != 0: data_in_width += 1
    if data_in_width > 512:
        raise Exception('Número máximo de nós ultrapassado!')

    m = Module('gnr_harp')
    clk = m.Input('clk_gnr')
    rst = m.Input('rst')
    start = m.Input('start')
    afu_context = m.Input('afu_context', 512)
    fifoin_empty = m.Input('fifoin_empty')
    fifoin_almost_empty = m.Input('fifoin_almost_empty')
    rd_fifoin_data = m.Input('rd_fifoin_data', 512)
    fifoout_full = m.Input('fifoout_full')
    fifo_out_almostfull = m.Input('fifo_out_almostfull')
    fifoout_empty = m.Input('fifoout_empty')
    rd_fifoin_en = m.Output('rd_fifoin_en')
    wr_fifoout_en = m.Output('wr_fifoout_en')
    wr_fifoout_data = m.Output('wr_fifoout_data', 512)
    done = m.Output('done')

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

    control_data_in = make_control_data_in(data_in_width, 512)
    con = [('clk', clk), ('rst', rst), ('start', start), ('num_data_in', num_data_in), ('has_data_in', ~fifoin_empty),
           ('has_lst3_data_in',fifoin_almost_empty),('data_in', rd_fifoin_data), ('rd_request_en', rd_fifoin_en),
           ('data_valid', data_in_valid),('data_out', data_in), ('done', end_data_in)]
    m.Instance(control_data_in, 'control_data_in', control_data_in.get_params(), con)

    rn = components.create_regulator_network(num_units, functions, fifo_in_size, fifo_out_size)
    for i in range(num_units):
        con = [('clk', clk), ('rst', rst), ('start', start), ('data_in_valid', data_in_valid),
               ('data_in', data_in[:data_in_width_con]),
               ('end_data_in', end_data_in),
               ('read_data_en', read_data_en[i]), ('has_data_out', has_data[i]),
               ('has_lst3_data_out', has_lst3_data[i]),
               ('data_out', data_out[i]),
               ('task_done', task_done[i])]
        m.Instance(rn, 'rn%d' % i, [('ID', i + 1)], con)

    control_data_out = make_control_data_out(num_units, data_width)
    con = [('clk', clk), ('rst', rst), ('start', start), ('num_data_out', num_data_out),
           ('fifo_out_full', fifoout_full),
           ('fifo_out_almostfull', fifo_out_almostfull), ('fifo_out_empty', fifoout_empty),
           ('has_data', has_data), ('has_lst3_data', has_lst3_data)]
    for i in range(num_units):
        if data_width - data_width_con > 0:
            con.append(('din%d' % i, Cat(Int(0, data_width - data_width_con, 10), data_out[i])))
        else:
            con.append(('din%d' % i,data_out[i]))

    for pair in [('read_data_en', read_data_en), ('task_done', task_done), ('wr_fifo_out_en', wr_fifoout_en),
                 ('wr_fifo_out_data', wr_fifoout_data), ('done', done)]:
        con.append(pair)

    m.Instance(control_data_out, 'control_data_out', control_data_out.get_params(), con)

    simulation.setup_waveform(m, 'gnr_harp')

    return m


path = '../../benchmarks/Benchmark_5.txt'
functions = readFile(path)
reg_net = RegulatorNetwork()
m = reg_net.create_regulator_network(1, functions, 16, 16)
m.to_verilog(m.name + ".v")