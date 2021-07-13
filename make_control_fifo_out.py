import math

from veriloggen import *


def make_control_fifo_out(data_width, num_units):
    m = Module('control_fifo_out')
    clk = m.Input('clk')
    rst = m.Input('rst')
    start = m.Input('start')
    num_data_out = m.Input('num_data_out', 32)
    task_done = m.Input('task_done', num_units)
    wr_en = m.Input('wr_en')
    wr_data = m.Input('wr_data', data_width)

    fifoout_full = m.Input('fifoout_full')
    fifoout_almostfull = m.Input('fifoout_almostfull')
    fifoout_empty = m.Input('fifoout_empty')
    wr_fifoout_en = m.OutputReg('wr_fifoout_en')
    wr_fifoout_data = m.Output('wr_fifoout_data', 512)
    done = m.OutputReg('done')

    bits = int(math.ceil(math.log((512 / data_width), 2)))
    if bits == 0:
        bits = 2
    else:
        bits = bits + 1
    index_data = m.Reg('index_data', bits)
    data = m.Reg('data', data_width, int(512 / data_width))
    count_empty = m.Reg('count_empty', 3)
    cont_data = m.Reg('cont_data', 32)

    fsm_cs = m.Reg('fms_cs', 3)
    buffer = m.Reg('buffer', data_width)

    i = m.Genvar('i')
    m.GenerateFor(i(0), i < (512 // data_width), i.inc(), 'gen_1').Assign(
        wr_fifoout_data[i * data_width:((i * data_width) + data_width)](data[i]))

    FSM_FIFO_WR = m.Localparam('FSM_FIFO_WR0', 1, 3)
    FSM_FIFO_FULL = m.Localparam('FSM_FIFO_FULL', 2, 3)
    FSM_END_DATA = m.Localparam('FSM_END_DATA', 3, 3)
    FSM_DONE = m.Localparam('FSM_DONE', 4, 3)

    m.Always(Posedge(clk))(
        If(rst)(
            fsm_cs(FSM_FIFO_WR),
            index_data(Int(0, bits, 10)),
            wr_fifoout_en(Int(0, 1, 2)),
            done(Int(0, 1, 2)),
            count_empty(Int(0, 3, 10)),
            buffer(Int(0, data_width, 10)),
            cont_data(Int(0, cont_data.width, 10))
        ).Elif(start)(
            wr_fifoout_en(Int(0, 1, 2)),
            Case(fsm_cs)(
                When(FSM_FIFO_WR)(
                    If(OrList(~task_done == Int(0, num_units, 10),(cont_data >= num_data_out)))(
                        If(index_data > 0)(
                            If(~fifoout_full)(
                                wr_fifoout_en(Int(1, 1, 2)),
                                index_data(Int(0, bits, 10)),
                                fsm_cs(FSM_END_DATA)
                            )
                        ).Else(
                            fsm_cs(FSM_END_DATA)
                        )
                    ).Elif(wr_en)(
                        If(index_data < (512 // data_width) - 1)(
                            data[index_data](wr_data),
                            index_data(index_data + Int(1,index_data.width,10))
                        ).Elif(~fifoout_full)(
                            data[index_data](wr_data),
                            wr_fifoout_en(Int(1, 1, 2)),
                            index_data(Int(0, bits, 10))
                        ).Else(
                            data[index_data](wr_data),
                            fsm_cs(FSM_FIFO_FULL)
                        ),
                        cont_data(cont_data + Int(1,cont_data.width,10))
                    )
                ),
                When(FSM_FIFO_FULL)(
                    If(wr_en)(
                        cont_data(cont_data + Int(1, cont_data.width, 10)),
                        buffer(wr_data)
                    ),
                    If(~fifoout_full)(
                        If(index_data >= (512 // data_width) - 1)(
                            wr_fifoout_en(Int(1, 1, 2)),
                            index_data(Int(0, bits, 10))
                        ).Else(

                            data[index_data](buffer),
                            index_data(index_data + Int(1,index_data.width,10)),
                            fsm_cs(FSM_FIFO_WR)
                        )
                    )
                ),
                When(FSM_END_DATA)(
                    If(count_empty > 2)(
                        fsm_cs(FSM_DONE),
                        done(Int(1, 1, 2))
                    ).Elif(fifoout_empty)(
                        count_empty(count_empty + Int(1,count_empty.width,10))
                    )
                ),
                When(FSM_DONE)(
                    fsm_cs(FSM_DONE),
                    done(Int(1, 1, 2))
                ),
            )
        )

    )

    return m
