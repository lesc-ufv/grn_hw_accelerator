from veriloggen import *


def make_control_gnr(number_nos, debug=False):
    m = Module("control_gnr")
    data_width = 29
    ID = m.Parameter('ID', 0)
    width = number_nos
    clk = m.Input('clk')
    rst = m.Input('rst')
    start = m.Input('start')

    s0 = m.Input('s0', width)
    s1 = m.Input('s1', width)

    fifo_out_full = m.Input('fifo_out_full')
    fifo_in_empty = m.Input('fifo_in_empty')
    fifo_data_in = m.Input('fifo_data_in', 2 * width)
    end_data_in = m.Input('end_data_in')
    fifo_in_re = m.OutputReg('fifo_in_re')
    start_s0 = m.OutputReg('start_s0')
    start_s1 = m.OutputReg('start_s1')
    reset_nos = m.OutputReg('reset_nos')
    init_state_out = m.OutputReg('init_state', width)
    fifo_out_we = m.OutputReg('fifo_out_we')
    fifo_out_empty = m.Input('fifo_out_empty')
    data_out = m.OutputReg('data_out', (data_width + data_width + width))
    done = m.OutputReg('done')

    state_net = m.Reg('state_net', width)
    period = m.Reg('period', data_width)
    transient = m.Reg('transient', data_width)

    end_state_reg = m.Reg('end_state_reg', width)
    period_count = m.Reg('period_count', data_width)
    transient_count = m.Reg('transient_count', data_width)
    start_count_period = m.Reg('start_count_period')
    start_count_transient = m.Reg('start_count_transient')
    reset_counts = m.Reg('reset_counts')
    pass_cycle = m.Reg('pass_cycle')
    state = m.Reg('fsm_state', 3)
    flag_rd = m.Reg('flag_rd')
    flag_wr = m.Reg('flag_wr')
    pass_cycle_attractor = m.Reg("pass_cycle_attractor")
    IDLE = m.Localparam('IDLE', 0)
    GET_STATE = m.Localparam('GET_STATE', 1)
    RESET_NOS = m.Localparam('RESET_NOS', 2)
    START_NOS = m.Localparam('START_NOS', 3)
    FIND_ATTRACTOR = m.Localparam('FIND_ATTRACTOR', 4)
    CALC_PERIOD_ATTRACTOR = m.Localparam('CALC_PERIOD_ATTRACTOR', 5)
    FIND_NEXT_ATTRACTOR = m.Localparam('FIND_NEXT_ATTRACTOR', 6)
    DONE = m.Localparam('DONE', 7)
    if debug:
        clk_count = m.Reg("clk_count", 64)
        m.Always(Posedge(clk))(
            If(rst)(
                clk_count(0),
            ).Elif(start)(
                clk_count.inc()
            )
        )

    m.Always(Posedge(clk))(
        If(rst)(
            init_state_out(Int(0, init_state_out.width, 10)),
            start_count_period(Int(0, 1, 2)),
            start_count_transient(Int(0, 1, 2)),
            done(Int(0, 1, 2)),
            start_s0(Int(0, 1, 2)),
            start_s1(Int(0, 1, 2)),
            fifo_out_we(Int(0, 1, 2)),
            reset_counts(Int(0, 1, 2)),
            state_net(Int(0, state_net.width, 10)),
            period(Int(0, period.width, 10)),
            transient(Int(0, transient.width, 10)),
            end_state_reg(Int(0, end_state_reg.width, 10)),
            fifo_in_re(Int(0, 1, 2)),
            flag_rd(Int(0, 1, 2)),
            flag_wr(Int(0, 1, 2)),
            reset_nos(Int(0, 1, 2)),
            data_out(Int(0, data_out.width, 10)),
            state(IDLE),
            pass_cycle_attractor(Int(1, 1, 2))
        ).Elif(start)(
            fifo_out_we(Int(0, 1, 2)),
            reset_nos(Int(0, 1, 2)),
            reset_counts(Int(0, 1, 2)),
            fifo_in_re(Int(0, 1, 2)),
            Case(state)(
                When(IDLE)(
                    If(~fifo_in_empty)(
                        fifo_in_re(Int(1, 1, 2)),
                        flag_rd(Int(0, 1, 2)),
                        state(GET_STATE)
                    ).Elif(end_data_in)(
                        state(DONE)
                    )
                ),
                When(GET_STATE)(
                    If(flag_rd)(
                        init_state_out(fifo_data_in[:width]),
                        end_state_reg(fifo_data_in[width:]),
                        flag_rd(Int(0, 1, 2)),
                        # Display("%d: ID: %d SET_STATE %d / %d", clk_count, ID, fifo_data_in[:width],
                        # fifo_data_in[width:]),
                        state(RESET_NOS)
                    ).Else(
                        flag_rd(Int(1, 1, 2))
                    )
                ),
                When(RESET_NOS)(
                    # Display("%d: ID: %d SET_STATE %d / %d", clk_count, ID, init_state_out, end_state_reg),
                    reset_nos(Int(1, 1, 2)),
                    reset_counts(Int(1, 1, 2)),
                    state(START_NOS),
                ),
                When(START_NOS)(
                    start_s0(Int(1, 1, 2)),
                    start_s1(Int(1, 1, 2)),
                    pass_cycle_attractor(Int(1, 1, 2)),
                    state(FIND_ATTRACTOR),
                    #   Display("%d: START_NOS", clk_count)
                ),
                When(FIND_ATTRACTOR)(
                    If(pass_cycle_attractor)(
                        pass_cycle_attractor(Int(0, 1, 2)),
                        If(AndList((s0 == s1), start_count_transient))(
                            state_net(s0),
                            If(s0 == init_state_out)(
                                transient(Int(0, transient.width, 10)),
                            ).Else(
                                transient(transient_count),
                            ),
                            start_count_transient(Int(0, 1, 2)),
                            start_s0(Int(0, 1, 2)),
                            start_s1(Int(0, 1, 2)),
                            state(CALC_PERIOD_ATTRACTOR),
                            #  Display("%d: FIND_ATTRACTOR -> CALC_PERIOD_ATTRACTOR: %x %x", clk_count, s0, s1)

                        ).Else(
                            start_count_transient(Int(1, 1, 2)),
                            state(FIND_ATTRACTOR),
                            #   Display("%d: FIND_ATTRACTOR -> FIND_ATTRACTOR: %x %x", clk_count, s0, s1)
                        )
                    ).Else(
                        pass_cycle_attractor(Int(1, 1, 2))
                    )
                ),
                When(CALC_PERIOD_ATTRACTOR)(
                    If(AndList((state_net == s1), start_count_period))(
                        start_count_period(Int(0, 1, 2)),
                        period(period_count),
                        start_s1(Int(0, 1, 2)),
                        state(FIND_NEXT_ATTRACTOR),
                        # Display("%d: CALC_PERIOD_ATTRACTOR -> FIND_NEXT_ATTRACTOR %x %x %d", clk_count, state_net, s1,
                        #      period)
                    ).Else(
                        state(CALC_PERIOD_ATTRACTOR),
                        start_count_period(Int(1, 1, 2)),
                        start_s1(Int(1, 1, 2)),
                        # Display("%d: CALC_PERIOD_ATTRACTOR -> CALC_PERIOD_ATTRACTOR %x %x %d", clk_count, state_net, s1,
                        #       period)
                    )
                ),
                When(FIND_NEXT_ATTRACTOR)(
                    If(~fifo_out_full)(
                        fifo_out_we(Int(1, 1, 2)),
                        data_out(Cat(state_net, transient, period)),
                        If(init_state_out < end_state_reg)(
                            init_state_out(init_state_out + Int(1, init_state_out.width, 10)),
                            state(RESET_NOS),
                            #    Display("%d: ID: %d FIND_NEXT_ATTRACTOR%d", clk_count, ID, init_state_out + 1)
                        ).Else(
                            state(DONE),
                            Display("%d: ID: %d DONE %d", 0, ID, init_state_out + 1)
                        )
                    )
                ),
                When(DONE)(
                    If(fifo_in_empty)(
                        If(end_data_in)(
                            If(flag_wr)(
                                If(fifo_out_empty)(
                                    done(Int(1, 1, 2))
                                ),
                                flag_wr(Int(0, 1, 2))
                            ).Else(
                                flag_wr(Int(1, 1, 2))
                            ),
                        ),
                        state(DONE)
                    ).Else(
                        fifo_in_re(Int(1, 1, 2)),
                        flag_rd(Int(0, 1, 2)),
                        init_state_out(Int(0, init_state_out.width, 10)),
                        state(GET_STATE)
                    )

                )
            )

        )
    )

    m.Always(Posedge(clk))(
        If(rst)(
            period_count(Int(0, period.width, 10)),
            transient_count(Int(0, transient_count.width, 10)),
            pass_cycle(Int(0, 1, 2))
        ).Elif(start)(
            If(reset_counts)(
                period_count(Int(0, period.width, 10)),
                transient_count(Int(0, transient_count.width, 10)),
                pass_cycle(Int(1, 1, 2))
            ).Else(
                If(pass_cycle)(
                    If(start_count_period)(
                        period_count(period_count + Int(1, period_count.width, 10))
                    ),
                    If(start_count_transient)(
                        transient_count(transient_count + Int(1, transient_count.width, 10)),
                        pass_cycle(Int(0, 1, 2))
                    )
                ).Else(
                    pass_cycle(Int(1, 1, 2))
                )
            )
        )
    )

    return m
