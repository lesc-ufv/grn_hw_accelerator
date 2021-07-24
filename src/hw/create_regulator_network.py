import math
from veriloggen import *
from src.hw.components import Components
from src.hw.utils import readFile


def make_regulator_network(num_units, functions, fifo_in_size, fifo_out_size):
    components = Components()

    m = Module("regulator_network")
    data_width = 29
    id = m.Parameter('id', 0)
    id_width = int(math.ceil(math.log(num_units, 2))) + 1
    width_data_in = 2 * len(functions) + id_width
    width = len(functions)
    fifo_in_depth_bits = int(math.ceil(math.log(fifo_in_size, 2)))
    fifo_out_depth_bits = int(math.ceil(math.log(fifo_out_size, 2)))

    clk = m.Input('clk')
    rst = m.Input('rst')
    start = m.Input('start')
    data_in_valid = m.Input('data_in_valid')
    data_in = m.Input('data_in', width_data_in)  # (id + BEGIN + END)
    end_data_in = m.Input('end_data_in')
    read_data_en = m.Input('read_data_en')
    has_data_out = m.Output('has_data_out')
    has_lst3_data_out = m.Output('has_lst3_data_out')
    data_out = m.Output('data_out', (data_width + data_width + width))
    task_done = m.Output('task_done')

    fifo_out_we = m.Wire('fifo_out_we')
    fifo_out_data_in = m.Wire('fifo_out_data_in',
                              (data_width + data_width + width))
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

    control_fifo_data_in = components.create_ctrl_fifo_data_in()
    param = [('id', id),
             ('id_width', int(math.ceil(math.log(num_units, 2))) + 1),
             ('width_data_in', width_data_in)]
    con = [('clk', clk), ('rst', rst), ('start', start),
           ('data_in_valid', data_in_valid), ('data_in', data_in),
           ('fifo_in_full', fifo_in_full), ('fifo_in_we', fifo_in_we),
           ('fifo_in_data', fifo_in_data_in)]
    m.Instance(control_fifo_data_in, '_' + control_fifo_data_in.name, param,
               con)

    fifo = components.create_fifo()
    param = [('fifo_width', width_data_in - id_width),
             ('fifo_depth_bits', fifo_in_depth_bits),
             ('fifo_almost_full_threshold', fifo_in_size - 2),
             ('fifo_almost_empty_threshold', 2)]
    con = [('clk', clk), ('rst', rst), ('we', fifo_in_we),
           ('din', fifo_in_data_in), ('re', fifo_in_re),
           ('dout', fifo_in_data_out), ('empty', fifo_in_empty),
           ('almostempty', fifo_in_almostempty), ('full', fifo_in_full),
           ('almostfull', fifo_in_full_almostfull)]
    m.Instance(fifo, 'fifo_in', param, con)

    param = [('fifo_width', (data_width + data_width + width)),
             ('fifo_depth_bits', fifo_out_depth_bits),
             ('fifo_almost_full_threshold', fifo_out_size - 2),
             ('fifo_almost_empty_threshold', 2)]
    con = [('clk', clk), ('rst', rst), ('we', fifo_out_we),
           ('din', fifo_out_data_in), ('re', read_data_en), ('dout', data_out),
           ('empty', fifo_out_empty), ('almostempty', has_lst3_data_out),
           ('full', fifo_out_full), ('almostfull', fifo_out_full_almostfull)]
    m.Instance(fifo, 'fifo_out', param, con)

    control = components.create_gnr_control(functions)
    con = [('clk', clk), ('rst', rst), ('start', start),
           ('fifo_out_full', fifo_out_full), ('fifo_in_empty', fifo_in_empty),
           ('fifo_data_in', fifo_in_data_out), ('end_data_in', end_data_in),
           ('fifo_in_re', fifo_in_re), ('data_out', fifo_out_data_in),
           ('fifo_out_we', fifo_out_we), ('fifo_out_empty', fifo_out_empty),
           ('done', task_done)]
    m.Instance(control, '_' + control.name, control.get_params(), con)

    return m


path = '../../benchmarks/Benchmark_5.txt'
functions = readFile(path)
m = make_regulator_network(1, functions, 16, 16)
m.to_verilog(m.name + ".v")
