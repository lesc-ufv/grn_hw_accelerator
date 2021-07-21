import math

from veriloggen import *

from create_control_fifo_data_in import make_control_fifo_data_in
from make_control_gnr import make_control_gnr
from make_fifo import make_fifo
from gnr_graph import maker_graph


def make_regulator_network(num_units, functions, fifo_in_size, fifo_out_size):
    m = Module("regulator_network")
    data_width = 29
    ID = m.Parameter('ID', 0)
    id_width = int(math.ceil(math.log(num_units, 2))) + 1
    width_data_in = 2 * len(functions) + id_width
    width = len(functions)
    fifo_in_depth_bits = int(math.ceil(math.log(fifo_in_size, 2)))
    fifo_out_depth_bits = int(math.ceil(math.log(fifo_out_size, 2)))

    clk = m.Input('clk')
    rst = m.Input('rst')
    start = m.Input('start')
    data_in_valid = m.Input('data_in_valid')
    data_in = m.Input('data_in', width_data_in)  # (ID + BEGIN + END)
    end_data_in = m.Input('end_data_in')
    read_data_en = m.Input('read_data_en')
    has_data_out = m.Output('has_data_out')
    has_lst3_data_out = m.Output('has_lst3_data_out')
    data_out = m.Output('data_out', (data_width + data_width + width))
    task_done = m.Output('task_done')

    s0 = m.Wire('s0', width)
    s1 = m.Wire('s1', width)
    start_s0 = m.Wire('start_s0')
    start_s1 = m.Wire('start_s1')
    reset_nos = m.Wire('reset_nos')
    init_state = m.Wire('init_state', width)

    fifo_out_we = m.Wire('fifo_out_we')
    fifo_out_data_in = m.Wire('fifo_out_data_in',(data_width + data_width + width))
    fifo_out_empty = m.Wire('fifo_out_empty')
    fifo_out_full = m.Wire('fifo_out_full')
    fifo_out_full_almostfull = m.Wire('fifo_out_full_almostfull')

    fifo_in_we = m.Wire('fifo_in_we')
    fifo_in_data_in = m.Wire('fifo_in_data_in', width_data_in - id_width)
    fifo_in_re = m.Wire('fifo_in_re')
    fifo_in_data_out = m.Wire('fifo_in_data_out', width_data_in - id_width)
    fifo_in_empty = m.Wire('fifo_in_empty')
    fifo_in_almostempty = m.Wire('fifo_in_almostempty')
    fifo_in_full = m.Wire('fifo_in_full')
    fifo_in_full_almostfull = m.Wire('fifo_in_full_almostfull')

    has_data_out.assign(~fifo_out_empty)

    control_fifo_data_in = make_control_fifo_data_in(num_units, width_data_in)
    con = [('clk', clk), ('rst', rst), ('start', start), ('data_in_valid', data_in_valid), ('data_in', data_in),
           ('fifo_in_full', fifo_in_full), ('fifo_in_amostfull', fifo_in_full_almostfull), ('fifo_in_we', fifo_in_we),
           ('fifo_in_data', fifo_in_data_in)]
    param = [('ID', ID)]

    m.Instance(control_fifo_data_in, 'control_fifo_data_in_', param, con)

    fifo = make_fifo()
    con = [('clk', clk), ('rst', rst), ('we', fifo_in_we), ('din', fifo_in_data_in),
           ('re', fifo_in_re), ('dout', fifo_in_data_out), ('empty', fifo_in_empty),
           ('almostempty', fifo_in_almostempty), ('full', fifo_in_full), ('almostfull', fifo_in_full_almostfull)]

    param = [('FIFO_WIDTH', width_data_in - id_width), ('FIFO_DEPTH_BITS', fifo_in_depth_bits),
             ('FIFO_ALMOSTFULL_THRESHOLD', fifo_in_size - 2),
             ('FIFO_ALMOSTEMPTY_THRESHOLD', 2)]

    m.Instance(fifo, 'fifo_in', param, con)

    con = [('clk', clk), ('rst', rst), ('we', fifo_out_we), ('din', fifo_out_data_in),
           ('re', read_data_en), ('dout', data_out), ('empty', fifo_out_empty),
           ('almostempty', has_lst3_data_out), ('full', fifo_out_full), ('almostfull', fifo_out_full_almostfull)]

    param = [('FIFO_WIDTH', (data_width + data_width + width)),
             ('FIFO_DEPTH_BITS', fifo_out_depth_bits),
             ('FIFO_ALMOSTFULL_THRESHOLD', fifo_out_size - 2),
             ('FIFO_ALMOSTEMPTY_THRESHOLD', 2)]

    m.Instance(fifo, 'fifo_out', param, con)

    control = make_control_gnr(len(functions))
    con = [('clk', clk), ('rst', rst), ('start', start), ('s0', s0), ('s1', s1), ('fifo_out_full', fifo_out_full),
           ('fifo_in_empty', fifo_in_empty), ('fifo_data_in', fifo_in_data_out), ('end_data_in', end_data_in),
           ('fifo_in_re', fifo_in_re),
           ('start_s0', start_s0), ('start_s1', start_s1), ('reset_nos', reset_nos), ('init_state', init_state),
           ('data_out', fifo_out_data_in), ('fifo_out_we', fifo_out_we), ('fifo_out_empty', fifo_out_empty),
           ('done', task_done)]

    m.Instance(control, 'control_gnr', control.get_params(), con)

    graph = maker_graph(functions)
    m.Instance(graph, 'network_graph', graph.get_params(), graph.get_ports())

    return m
