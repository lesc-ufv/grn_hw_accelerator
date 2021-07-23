import math
from veriloggen import *


def make_control_fifo_data_in(num_units, width_data_in):
    m = Module('control_fifo_data_in')
    ID = m.Parameter('ID', 0)
    clk = m.Input('clk')
    rst = m.Input('rst')
    start = m.Input('start')
    data_in_valid = m.Input('data_in_valid')
    data_in = m.Input('data_in', width_data_in)  # (ID + BEGIN + END)
    id_width = int(math.ceil(math.log(num_units, 2))) + 1
    fifo_in_full = m.Input('fifo_in_full')
    fifo_in_amostfull = m.Input('fifo_in_amostfull')
    fifo_in_we = m.OutputReg('fifo_in_we')
    fifo_in_data = m.OutputReg('fifo_in_data', width_data_in - id_width)

    m.Always(Posedge(clk))(
        If(rst)(
            fifo_in_we(Int(0, 1, 2)),
            fifo_in_data(Int(0, fifo_in_data.width, 10))
        ).Elif(start)(
            fifo_in_we(Int(0, 1, 2)),
            If(AndList(data_in_valid, (data_in[:id_width] == ID), (~fifo_in_full)))(
                fifo_in_we(Int(1, 1, 2)),
                fifo_in_data(data_in[id_width:])
            )
        )

    )
    return m
