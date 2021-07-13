import math

from veriloggen import *


def make_control_data_in(data_width, data_width_ext):
    m = Module('control_data_in')
    clk = m.Input('clk')
    rst = m.Input('rst')
    start = m.Input('start')
    num_data_in = m.Input('num_data_in', 32)
    has_data_in = m.Input('has_data_in')
    has_lst3_data_in = m.Input('has_lst3_data_in')
    data_in = m.Input('data_in', 512)
    rd_request_en = m.OutputReg('rd_request_en')
    data_valid = m.OutputReg('data_valid')
    data_out = m.OutputReg('data_out', data_width)
    done = m.OutputReg('done')

    bits = int(math.ceil(math.log((data_width_ext // (data_width)), 2)))
    if bits == 0:
        bits = 2
    else:
        bits = bits + 1

    FSM_WAIT = m.Localparam('FSM_WAIT', 0, 3)
    FSM_RD_DATA = m.Localparam('FSM_RD_DATA', 1, 3)
    FSM_DONE = m.Localparam('FSM_DONE', 2, 3)
    fsm_cs = m.Reg('fms_cs', 3)
    cont_data = m.Reg('cont_data', 32)

    if data_width < 512:
        index_data = m.Reg('index_data', bits)
        data = m.Reg('data', data_width_ext)
        flag_cpy_data = m.Reg('flag_cpy_data')
        wdata = m.Wire('wdata', data_width, data_width_ext // data_width)

        i = m.Genvar('i')
        m.GenerateFor(i(0), i < (data_width_ext // data_width), i.inc(), 'gen_1').Assign(
            wdata[i](data[i * data_width:(i * data_width) + data_width])
        )
        m.Always(Posedge(clk))(
            If(rst)(
                rd_request_en(Int(0, 1, 2)),
                index_data(Int(0, index_data.width, 10)),
                data(Int(0, data.width, 10)),
                data_out(Int(0, data_out.width, 10)),
                cont_data(Int(0, cont_data.width, 10)),
                flag_cpy_data(Int(0, 1, 2)),
                done(Int(0, 1, 2)),
                data_valid(Int(0, 1, 2)),
                fsm_cs(FSM_WAIT),
            ).Elif(start)(
                data_valid(Int(0, 1, 2)),
                rd_request_en(Int(0, 1, 2)),
                Case(fsm_cs)(
                    When(FSM_WAIT)(
                        If(cont_data < num_data_in)(
                            If(AndList((index_data < (data_width_ext // data_width)), flag_cpy_data))(
                                data_out(Int(0, data_out.width, 10)),
                                fsm_cs(FSM_RD_DATA)
                            ).Elif(has_data_in)(
                                rd_request_en(Int(1, 1, 2)),
                                index_data(Int(0,index_data.width,10)),
                                flag_cpy_data(Int(0, 1, 2)),
                                data_out(Int(0, data_out.width, 10)),
                                fsm_cs(FSM_RD_DATA)
                            ).Else(
                                data_out(Int(0, data_out.width, 10)),
                                fsm_cs(FSM_WAIT)
                            )
                        ).Else(
                            data_out(Int(0, data_out.width, 10)),
                            fsm_cs(FSM_DONE),
                        )
                    ),
                    When(FSM_RD_DATA)(
                        If(flag_cpy_data == Int(0, 1, 2))(
                            data(data_in),
                            data_out(data_in[0:data_width]),
                            flag_cpy_data(Int(1, 1, 2)),
                            data_valid(Int(1, 1, 2)),
                            cont_data(cont_data+Int(1,cont_data.width,10)),
                            index_data(index_data + Int(1, index_data.width, 10)),
                            fsm_cs(FSM_WAIT)
                        ).Else(
                            data_out(wdata[index_data]),
                            data_valid(Int(1, 1, 2)),
                            cont_data(cont_data+Int(1,cont_data.width,10)),
                            index_data(index_data + Int(1, index_data.width, 10)),
                            fsm_cs(FSM_WAIT)
                        )
                    ),
                    When(FSM_DONE)(
                        data_out(Int(0, data_out.width, 10)),
                        fsm_cs(FSM_DONE),
                        done(Int(1, 1, 2))
                    )
                )
            )
        )
    else:
        m.Always(Posedge(clk))(
            If(rst)(
                rd_request_en(Int(0, 1, 2)),
                data_out(Int(0, data_out.width, 10)),
                cont_data(Int(0, cont_data.width, 10)),
                done(Int(0, 1, 2)),
                data_valid(Int(0, 1, 2)),
                fsm_cs(FSM_WAIT),
            ).Elif(start)(
                data_valid(Int(0, 1, 2)),
                rd_request_en(Int(0, 1, 2)),
                Case(fsm_cs)(
                    When(FSM_WAIT)(
                        If(cont_data < num_data_in)(
                            If(has_data_in)(
                                rd_request_en(Int(1, 1, 2)),
                                data_out(Int(0, data_out.width, 10)),
                                fsm_cs(FSM_RD_DATA)
                            ).Else(
                                data_out(Int(0, data_out.width, 10)),
                                fsm_cs(FSM_WAIT)
                            )
                        ).Else(
                            data_out(Int(0, data_out.width, 10)),
                            fsm_cs(FSM_DONE),
                        )
                    ),
                    When(FSM_RD_DATA)(
                        data_out(data_in),
                        cont_data(cont_data + Int(1, cont_data.width, 10)),
                        data_valid(Int(1, 1, 2)),
                        fsm_cs(FSM_WAIT)
                    ),
                    When(FSM_DONE)(
                        data_out(Int(0, data_out.width, 10)),
                        fsm_cs(FSM_DONE),
                        done(Int(1, 1, 2))
                    )
                )
            )
        )

    return m
