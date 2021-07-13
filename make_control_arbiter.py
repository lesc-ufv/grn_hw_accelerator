import math

from veriloggen import *

from make_arbiter import make_arbiter


def make_control_arbiter(num_units):
    m = Module('control_arbiter')
    bits = int(math.ceil(math.log(num_units, 2)))
    clk = m.Input('clk')
    rst = m.Input('rst')
    start = m.Input('start')
    has_data_out = m.Input('has_data_out', num_units)
    has_lst3_data = m.Input('has_lst3_data', num_units)
    fifo_out_full = m.Input('fifo_out_full')
    wr_fifo_out = Reg()
    wr_fifo_out_reg = Reg()
    read_data_en = Reg()
    if num_units == 1:
        read_data_en = m.OutputReg('read_data_en', num_units)
        wr_fifo_out = m.OutputReg('wr_fifo_out')
        wr_fifo_out_reg = m.Reg('wr_fifo_out_reg')

    if num_units > 1:

        read_data_en = m.OutputReg('read_data_en', num_units)
        wr_fifo_out = m.OutputReg('wr_fifo_out')
        mux_control = m.OutputReg('mux_control', bits)

        FSM_IDLE = m.Localparam('FSM_IDLE', 0)
        FSM_RD_REQ = m.Localparam('FSM_RD_REQ', 1)
        FSM_WR_REQ = m.Localparam('FSM_WR_REQ', 2)
        fsm_state = m.Reg('fsm_state', 3)
        request = m.Reg('request',num_units)
        grant_index_reg = m.Reg('grant_index_reg',bits)

        grant = m.Wire('grant', num_units)
        grant_index = m.Wire('grant_index', bits)
        grant_valid = m.Wire('grant_valid')


        arbiter = make_arbiter()
        params = [('PORTS', num_units), ('TYPE', "ROUND_ROBIN"), ('BLOCK', "NONE"), ('LSB_PRIORITY', "LOW")]
        ports = [('clk', clk), ('rst', rst), ('request', request),
                 ('acknowledge', Int(0, num_units, 10)),
                 ('grant', grant),
                 ('grant_valid', grant_valid),
                 ('grant_encoded', grant_index)]

        m.Instance(arbiter, 'arbiter_inst', params, ports)

        m.Always(Posedge(clk))(
            If(rst)(
                fsm_state(FSM_IDLE),
                request(Int(0,request.width,10)),
                read_data_en(Int(0,1,2)),
                grant_index_reg(Int(0,grant_index.width,10)),
                wr_fifo_out(Int(0, 1, 2)),
                mux_control(Int(0,mux_control.width,10)),
            ).Elif(start)(
                request(Int(0, request.width, 10)),
                read_data_en(Int(0, 1, 2)),
                wr_fifo_out(Int(0, 1, 2)),
                mux_control(Int(0, mux_control.width, 10)),
                Case(fsm_state)(
                    When(FSM_IDLE)(
                        If(AndList(has_data_out != Int(0, has_data_out.width, 10), Not(fifo_out_full)))(
                            request(has_data_out),
                            fsm_state(FSM_RD_REQ)
                        )
                    ),
                    When(FSM_RD_REQ)(
                        If(grant_valid)(
                            read_data_en(grant),
                            grant_index_reg(grant_index),
                            fsm_state(FSM_WR_REQ)
                        )
                    ),
                    When(FSM_WR_REQ)(
                        wr_fifo_out(Int(1,1,2)),
                        mux_control(grant_index_reg),
                        fsm_state(FSM_IDLE)
                    )
                )
            )
        )

    else:
        flag_rd = m.Reg('flag_rd')
        m.Always(Posedge(clk))(
            If(rst)(
                wr_fifo_out(Int(0, 1, 2))
            ).Elif(start)(
                wr_fifo_out(wr_fifo_out_reg)
            )
        )
        m.Always(Posedge(clk))(
            If(rst)(
                read_data_en(Int(0, num_units, 10)),
                wr_fifo_out_reg(Int(0, 1, 2)),
                flag_rd(1),
            ).Elif(start)(
                read_data_en(Int(0, num_units, 10)),
                wr_fifo_out_reg(Int(0, 1, 2)),
                If(AndList(has_data_out != Int(0, num_units, 10), ~fifo_out_full))(
                    If(has_lst3_data)(
                        If(flag_rd)(
                            flag_rd(0),
                            read_data_en(Int(1, read_data_en.width, 2)),
                            wr_fifo_out_reg(Int(1, 1, 2)),
                        ).Else(
                            flag_rd(1)
                        )
                    ).Else(
                        read_data_en(Int(1, read_data_en.width, 2)),
                        wr_fifo_out_reg(Int(1, 1, 2)),
                    )
                )
            )
        )

    return m
