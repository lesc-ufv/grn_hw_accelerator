import math

from veriloggen import *

from make_control_fifo_out import make_control_fifo_out
from make_control_arbiter import make_control_arbiter
from make_mux import make_mux


def make_control_data_out(num_units, data_width):
    m = Module('control_data_out')
    clk = m.Input('clk')
    rst = m.Input('rst')
    start = m.Input('start')
    num_data_out = m.Input('num_data_out', 32)
    fifo_out_full = m.Input('fifo_out_full')
    fifo_out_almostfull = m.Input('fifo_out_almostfull')
    fifo_out_empty = m.Input('fifo_out_empty')
    has_data = m.Input('has_data', num_units)
    has_lst3_data = m.Input('has_lst3_data', num_units)
    ports_in = {}
    for p in range(num_units):
        ports_in['din%d' % p] = m.Input('din%d' % p, data_width)
    task_done = m.Input('task_done', num_units)
    wr_fifo_out_en = m.Output('wr_fifo_out_en')
    wr_fifo_out_data = m.Output('wr_fifo_out_data', 512)
    if num_units == 1:
        read_data_en = m.OutputReg('read_data_en', num_units)
    else:
        read_data_en = m.Output('read_data_en', num_units)
    done = m.Output('done')

    if num_units > 1:
        wr_fifo_out = m.Wire('wr_fifo_out')
        con = [('clk', clk), ('rst', rst), ('start', start), ('has_data_out', has_data),
               ('has_lst3_data', has_lst3_data), ('fifo_out_full', fifo_out_full),
               ('read_data_en', read_data_en), ('wr_fifo_out', wr_fifo_out)]
        mux_num_bits = int(math.ceil(math.log(num_units, 2)))
        mux_control = m.Wire('mux_control', mux_num_bits)
        mux_data_out = m.Wire('mux_data_out', data_width)
        con.append(('mux_control', mux_control))
        control_arbiter = make_control_arbiter(num_units)
        m.Instance(control_arbiter, 'control_arbiter', control_arbiter.get_params(), con)
        mux_wr_fifo_out = make_mux(num_units, data_width)
        con = []
        for i in range(num_units):
            con.append(('in%d' % i, ports_in.get('din%d' % i)))
        con.append(('s', mux_control))
        con.append(('out', mux_data_out))
        m.Instance(mux_wr_fifo_out, 'mux_wr_fifo_out', [('WIDTH', data_width)], con)

        control_fifo_out = make_control_fifo_out(data_width, num_units)
        con = [('clk', clk), ('rst', rst), ('start', start), ('num_data_out', num_data_out), ('task_done', task_done),
               ('wr_en', wr_fifo_out), ('wr_data', mux_data_out), ('fifoout_full', fifo_out_full),
               ('fifoout_almostfull', fifo_out_almostfull), ('fifoout_empty', fifo_out_empty),
               ('wr_fifoout_en', wr_fifo_out_en), ('wr_fifoout_data', wr_fifo_out_data), ('done', done)]
    else:
        wr_fifo_out = m.Reg("wr_fifo_out")
        flag_pass   = m.Reg('flag_pass')
        m.Always(Posedge(clk))(
            If(rst)(
                read_data_en(Int(0, 1, 2)),
                wr_fifo_out(Int(0, 1, 2)),
                flag_pass(Int(1, 1, 2))
            ).Elif(start)(
                read_data_en(Int(0, 1, 2)),
                wr_fifo_out(Int(0, 1, 2)),
                If(has_data)(
                    If(has_lst3_data)(
                        If(flag_pass)(
                            flag_pass(Int(0, 1, 2)),
                            read_data_en(Int(1, 1, 2))
                        ).Else(
                            flag_pass(Int(1, 1, 2))
                        )
                    ).Else(
                        read_data_en(Int(1,1,2))
                    )
                ),
                If(read_data_en)(
                    wr_fifo_out(Int(1,1,2))
                )

            )
        )
        control_fifo_out = make_control_fifo_out(data_width, num_units)
        con = [('clk', clk), ('rst', rst), ('start', start), ('num_data_out', num_data_out), ('task_done', task_done),
               ('wr_en', wr_fifo_out), ('wr_data', ports_in.get('din0')), ('fifoout_full', fifo_out_full),
               ('fifoout_almostfull', fifo_out_almostfull), ('fifoout_empty', fifo_out_empty),
               ('wr_fifoout_en', wr_fifo_out_en), ('wr_fifoout_data', wr_fifo_out_data), ('done', done)]



    m.Instance(control_fifo_out, 'control_fifo_out', control_fifo_out.get_params(), con)

    return m
