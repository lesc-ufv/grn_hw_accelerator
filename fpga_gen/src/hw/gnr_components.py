import math

from veriloggen import *
from veriloggen import Uand

from fpga_gen.src.hw.utils import initialize_regs


class GnrComponents:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.cache = {}

    def create_no(self, funcao, debug=False):
        name = funcao.split('=')[0].replace(' ', '')

        mod_name = 'no_%s' % name
        if mod_name in self.cache.keys():
            return self.cache[mod_name]

        m = Module(mod_name)
        clk = m.Input('clk')
        start = m.Input('start')
        rst = m.Input('rst')
        reset = m.Input('reset_nos')
        start_s0 = m.Input('start_s0')
        start_s1 = m.Input('start_s1')
        init_state = m.Input('init_state')
        ops = {'and': ' & ', 'or': ' | ', 'not': ' ~ ', 'xor': ' ^ ', 'nor': ' ~| ', 'nand': ' ~& ', 'xnor': ' ~^ '}

        funcao_orig = funcao
        funcao = re.sub(u'[()]', '', funcao)
        funcao = funcao.split("=")[1].split(" ")
        ops1 = ops.keys()
        port_names = []
        for port in funcao:
            if port not in ops1 and port != "":
                if port != name and port not in port_names:
                    m.Input(port + '_s0', 1)
                    m.Input(port + '_s1', 1)
                    port_names.append(port)

        for op in ops1:
            token = ' ' + op + ' '
            if token in funcao_orig:
                op2 = ops.get(op)
                funcao_orig = re.sub(token, op2, funcao_orig)

        funcao_orig_s0 = funcao_orig
        funcao_orig_s1 = funcao_orig

        for p in port_names:
            token = ' ' + p + ' '
            if token in funcao_orig:
                funcao_orig_s0 = re.sub(token, ' ' + p + '_s0 ', funcao_orig_s0)
                funcao_orig_s1 = re.sub(token, ' ' + p + '_s1 ', funcao_orig_s1)

        token = ' ' + name + ' '
        funcao_orig_s0 = re.sub(token, ' s0 ', funcao_orig_s0)
        funcao_orig_s1 = re.sub(token, ' s1 ', funcao_orig_s1)

        funcao_orig_s0 = funcao_orig_s0.split('=')[1]
        funcao_orig_s1 = funcao_orig_s1.split('=')[1]

        passs = m.Reg('pass')

        s0 = m.OutputReg('s0', 1)
        s1 = m.OutputReg('s1', 1)
        out_s0 = m.Output(name + '_s0', 1)
        out_s1 = m.Output(name + '_s1', 1)

        if debug:
            clk_count = m.Reg("clk_count", 64)

            m.Always(Posedge(clk))(
                If(reset)(
                    clk_count(0),
                ).Elif(start)(
                    clk_count.inc()
                )
            )

            '''m.Always(s0)(
                Display("%d: NO %s s0: %d s0 next: %d", clk_count, name, s0, EmbeddedNumeric(funcao_orig_s0))
            )
            m.Always(s1)(
                Display("%d: NO %s s1: %d s1 next: %d", clk_count, name, s1, EmbeddedNumeric(funcao_orig_s1))
            )'''

        m.Always(Posedge(clk))(
            If(rst)(
                s0(Int(0, s0.width, 10)),
                passs(Int(0, 1, 2))
            ).Elif(reset)(
                s0(init_state),
                passs(1),
                # Display("%d: RESET NO s0 %s %d", clk_count, name, init_state)
            ).Elif(start_s0)(
                If(passs)(
                    s0(EmbeddedNumeric(funcao_orig_s0)),
                    passs(0)
                    # Display("%d: NO %s s0: %d s0 next: %d",clk_count, name, s0, EmbeddedNumeric(funcaoB_s0))
                ).Else(
                    passs(1)
                )
            )
        )
        m.Always(Posedge(clk))(
            If(rst)(
                s1(Int(0, s1.width, 10))
            ).Elif(reset)(
                s1(init_state)
            ).Elif(start_s1)(
                s1(EmbeddedNumeric(funcao_orig_s1))
                # Display("%d: NO %s s1: %d s1 next: %d",clk_count ,name, s1, EmbeddedNumeric(funcaoB_s1))
            )
        )
        m.Assign(out_s0(s0))
        m.Assign(out_s1(s1))

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_graph(self, functions):
        name = 'network_graph'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        width = len(functions)
        m.Input('clk')
        m.Input('rst')
        m.Input('start')
        m.Input('reset_nos')
        m.Input('start_s0')
        m.Input('start_s1')
        m.Input('init_state', width)
        m.Output('s0', width)
        m.Output('s1', width)

        for f in functions:
            wire = f.split('=')[0].replace(' ', '')
            m.Wire(wire + '_s0')
            m.Wire(wire + '_s1')

        i = 0
        ports_graph_genes = m.get_ports()
        wires_graph_genes = m.get_vars()
        for f in functions:
            no = self.create_no(f)
            ports_no = no.get_ports()
            ports_con = []
            for p in ports_no:
                if p in ports_graph_genes:
                    p2p = ports_graph_genes.get(p)
                else:
                    p2p = wires_graph_genes.get(p)

                if p2p.width:
                    if p2p.width > 1:
                        p2p = p2p[i]
                ports_con.append((p, p2p))
            i += 1

            m.Instance(no, "_%s" % no.name, no.get_params(), ports_con)

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_control_fifo_data_in(self, width_data_in, id_width):
        name = 'control_fifo_data_in'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        ID = m.Parameter('ID', 0)
        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')
        data_in_valid = m.Input('data_in_valid')
        data_in = m.Input('data_in', width_data_in)  # (ID + BEGIN + END)
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
                If(AndList(data_in_valid, (data_in[width_data_in - id_width:width_data_in] == ID), (~fifo_in_full)))(
                    fifo_in_we(Int(1, 1, 2)),
                    fifo_in_data(data_in[:id_width])
                )
            )

        )

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_fifo(self):
        name = 'fifo'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        FIFO_WIDTH = m.Parameter('FIFO_WIDTH', 32)
        FIFO_DEPTH_BITS = m.Parameter('FIFO_DEPTH_BITS', 8)
        FIFO_ALMOSTFULL_THRESHOLD = m.Parameter('FIFO_ALMOSTFULL_THRESHOLD', EmbeddedNumeric('2**FIFO_DEPTH_BITS - 4'))
        FIFO_ALMOSTEMPTY_THRESHOLD = m.Parameter('FIFO_ALMOSTEMPTY_THRESHOLD', 2)

        clk = m.Input('clk')
        rst = m.Input('rst')
        we = m.Input('we')
        din = m.Input('din', FIFO_WIDTH)
        re = m.Input('re')
        dout = m.OutputReg('dout', FIFO_WIDTH)
        empty = m.OutputReg('empty')
        almostempty = m.OutputReg('almostempty')
        full = m.OutputReg('full')
        almostfull = m.OutputReg('almostfull')

        rp = m.Reg('rp', FIFO_DEPTH_BITS)
        wp = m.Reg('wp', FIFO_DEPTH_BITS)
        count = m.Reg('count', FIFO_DEPTH_BITS)
        mem = m.Reg('mem', FIFO_WIDTH, EmbeddedNumeric('2**FIFO_DEPTH_BITS'))

        m.Always(Posedge(clk))(
            If(rst)(
                empty(Int(1, 1, 2)),
                almostempty(Int(1, 1, 2)),
                full(Int(0, 1, 2)),
                almostfull(Int(0, 1, 2)),
                rp(0),
                wp(0),
                count(0)
            ).Else(
                Case(Cat(we, re))(
                    When(Int(3, 2, 2))(
                        rp.inc(),
                        wp.inc(),
                    ),
                    When(Int(2, 2, 2))(
                        If(~full)(
                            wp.inc(),
                            count.inc(),
                            empty(Int(0, 1, 2)),
                            If(count == (FIFO_ALMOSTEMPTY_THRESHOLD - 1))(
                                almostempty(Int(0, 1, 2))
                            ),
                            If(count == EmbeddedNumeric('2**FIFO_DEPTH_BITS-1'))(
                                full(Int(1, 1, 2))
                            ),
                            If(count == (FIFO_ALMOSTFULL_THRESHOLD - 1))(
                                almostfull(Int(1, 1, 2))
                            )
                        )

                    ),
                    When(Int(1, 2, 2))(
                        If(~empty)(
                            rp.inc(),
                            count(count - 1),
                            full(Int(0, 1, 2)),
                            If(count == FIFO_ALMOSTFULL_THRESHOLD)(
                                almostfull(Int(0, 1, 2))
                            ),
                            If(count == 1)(
                                empty(Int(1, 1, 2))
                            ),
                            If(count == FIFO_ALMOSTEMPTY_THRESHOLD)(
                                almostempty(Int(1, 1, 2))
                            )

                        )
                    )
                )
            )
        )
        m.Always(Posedge(clk))(
            If(rst)(
                dout(0),
            ).Else(
                If(we == Int(1, 1, 2))(
                    mem[wp](din)
                ),
                If(re == Int(1, 1, 2))(
                    dout(mem[rp])
                )
            )
        )

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_control_gnr(self, number_nos, debug=False):
        name = 'control_gnr'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
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

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_regulator_network(self, num_units, functions, fifo_in_size, fifo_out_size, id_width, data_in_width,
                                 data_out_width):
        name = 'regulator_network'
        if name in self.cache.keys():
            return self.cache[name]

        width = len(functions)

        m = Module(name)

        fifo_in_depth_bits = int(math.ceil(math.log(fifo_in_size, 2)))
        fifo_out_depth_bits = int(math.ceil(math.log(fifo_out_size, 2)))

        ID = m.Parameter('ID', 0)
        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')
        control_data_in_done = m.Input('control_data_in_done')

        data_in_valid = m.Input('data_in_valid')
        data_in = m.Input('data_in', data_in_width)  # (ID + BEGIN + END)
        end_data_in = m.Input('end_data_in')

        read_data_en = m.Input('read_data_en')
        has_data_out = m.Output('has_data_out')
        has_lst3_data_out = m.Output('has_lst3_data_out')
        data_out = m.Output('data_out', data_out_width)
        task_done = m.Output('task_done')

        s0 = m.Wire('s0', width)
        s1 = m.Wire('s1', width)
        start_s0 = m.Wire('start_s0')
        start_s1 = m.Wire('start_s1')
        reset_nos = m.Wire('reset_nos')
        init_state = m.Wire('init_state', width)

        fifo_out_we = m.Wire('fifo_out_we')
        fifo_out_data_in = m.Wire('fifo_out_data_in', data_out_width)
        fifo_out_empty = m.Wire('fifo_out_empty')
        fifo_out_full = m.Wire('fifo_out_full')
        fifo_out_full_almostfull = m.Wire('fifo_out_full_almostfull')

        fifo_in_we = m.Wire('fifo_in_we')
        fifo_in_data_in = m.Wire('fifo_in_data_in', data_in_width - id_width)
        fifo_in_re = m.Wire('fifo_in_re')
        fifo_in_data_out = m.Wire('fifo_in_data_out', data_in_width - id_width)
        fifo_in_empty = m.Wire('fifo_in_empty')
        fifo_in_almostempty = m.Wire('fifo_in_almostempty')
        fifo_in_full = m.Wire('fifo_in_full')
        fifo_in_full_almostfull = m.Wire('fifo_in_full_almostfull')

        has_data_out.assign(~fifo_out_empty)

        control_fifo_data_in = self.create_control_fifo_data_in(data_in_width, id_width)
        con = [('clk', clk), ('rst', rst), ('start', start), ('data_in_valid', data_in_valid), ('data_in', data_in),
               ('fifo_in_full', fifo_in_full), ('fifo_in_amostfull', fifo_in_full_almostfull),
               ('fifo_in_we', fifo_in_we),
               ('fifo_in_data', fifo_in_data_in)]
        param = [('ID', ID)]

        m.Instance(control_fifo_data_in, 'control_fifo_data_in_', param, con)

        fifo = self.create_fifo()
        con = [('clk', clk), ('rst', rst), ('we', fifo_in_we), ('din', fifo_in_data_in),
               ('re', fifo_in_re), ('dout', fifo_in_data_out), ('empty', fifo_in_empty),
               ('almostempty', fifo_in_almostempty), ('full', fifo_in_full), ('almostfull', fifo_in_full_almostfull)]

        param = [('FIFO_WIDTH', data_in_width - id_width), ('FIFO_DEPTH_BITS', fifo_in_depth_bits),
                 ('FIFO_ALMOSTFULL_THRESHOLD', fifo_in_size - 2),
                 ('FIFO_ALMOSTEMPTY_THRESHOLD', 2)]
        m.Instance(fifo, 'fifo_in', param, con)

        con = [('clk', clk), ('rst', rst), ('we', fifo_out_we), ('din', fifo_out_data_in),
               ('re', read_data_en), ('dout', data_out), ('empty', fifo_out_empty),
               ('almostempty', has_lst3_data_out), ('full', fifo_out_full), ('almostfull', fifo_out_full_almostfull)]

        param = [('FIFO_WIDTH', data_out_width),
                 ('FIFO_DEPTH_BITS', fifo_out_depth_bits),
                 ('FIFO_ALMOSTFULL_THRESHOLD', fifo_out_size - 2),
                 ('FIFO_ALMOSTEMPTY_THRESHOLD', 2)]
        m.Instance(fifo, 'fifo_out', param, con)

        control = self.create_control_gnr(len(functions))
        con = [('clk', clk), ('rst', rst), ('start', start), ('s0', s0), ('s1', s1), ('fifo_out_full', fifo_out_full),
               ('fifo_in_empty', fifo_in_empty), ('fifo_data_in', fifo_in_data_out), ('end_data_in', end_data_in),
               ('fifo_in_re', fifo_in_re),
               ('start_s0', start_s0), ('start_s1', start_s1), ('reset_nos', reset_nos), ('init_state', init_state),
               ('data_out', fifo_out_data_in), ('fifo_out_we', fifo_out_we), ('fifo_out_empty', fifo_out_empty),
               ('done', task_done)]

        m.Instance(control, 'control_gnr', control.get_params(), con)

        graph = self.create_graph(functions)
        m.Instance(graph, 'network_graph', graph.get_params(), graph.get_ports())

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_control_data_in(self, data_in_width):
        name = 'control_data_in'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')
        gnr_read_data_valid = m.Input('gnr_read_data_valid')
        gnr_read_data = m.Input('gnr_read_data', data_in_width)
        gnr_done_rd_data = m.Input('gnr_done_rd_data')
        gnr_request_read = m.OutputReg('gnr_request_read')
        data_valid = m.OutputReg('data_valid')
        data_out = m.OutputReg('data_out', data_in_width)
        done = m.OutputReg('done')

        FSM_SEND_DATA = m.Localparam('FSM_SEND_DATA', 0, 2)
        FSM_DONE = m.Localparam('FSM_DONE', 1, 2)
        fsm_cs = m.Reg('fms_cs', 2)

        m.Always(Posedge(clk))(
            If(rst)(
                gnr_request_read(0),
                done(0),
                data_valid(0),
                fsm_cs(FSM_SEND_DATA),
            ).Elif(start)(
                data_valid(0),
                gnr_request_read(0),
                Case(fsm_cs)(
                    When(FSM_SEND_DATA)(
                        If(gnr_done_rd_data)(
                            fsm_cs(FSM_DONE),
                        ).Elif(gnr_read_data_valid)(
                            data_out(gnr_read_data),
                            gnr_request_read(1),
                        ),
                    ),
                    When(FSM_DONE)(
                        done(1)
                    )
                )
            )
        )

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_priority_encoder(self):
        name = 'priority_encoder'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        WIDTH = m.Parameter('WIDTH', 4)
        LSB_PRIORITY = m.Parameter('LSB_PRIORITY', "LOW")
        input_unencoded = m.Input('input_unencoded', WIDTH)
        output_valid = m.Output('output_valid', 1)
        output_encoded = m.Output('output_encoded', EmbeddedCode('$clog2(WIDTH)'))
        output_unencoded = m.Output('output_unencoded', WIDTH)

        W1 = m.Localparam('W1', EmbeddedCode('2**$clog2(WIDTH)'))
        W2 = m.Localparam('W2', EmbeddedCode('W1/2'))

        gen_if = m.GenerateIf(WIDTH == 2, 'if_width')
        gen_if.Assign(output_valid(input_unencoded[0] | input_unencoded[1]))
        gen_if2 = gen_if.GenerateIf(LSB_PRIORITY == 'LOW', 'if_low')
        gen_if2.Assign(output_encoded(input_unencoded[1]))
        gen_if2 = gen_if2.Else('else_low')
        gen_if2.EmbeddedCode('assign output_encoded = ~input_unencoded[0];')
        gen_if = gen_if.Else('else_width')
        gen_if.Wire('out1', EmbeddedCode('$clog2(W2)'))
        gen_if.Wire('out2', EmbeddedCode('$clog2(W2)'))
        gen_if.Wire('valid1')
        gen_if.Wire('valid2')
        gen_if.Wire('out_un', WIDTH)
        gen_if.EmbeddedCode('priority_encoder #(\n\
                    .WIDTH(W2),\n\
                    .LSB_PRIORITY(LSB_PRIORITY)\n\
                )\n\
                priority_encoder_inst1 (\n\
                    .input_unencoded(input_unencoded[W2-1:0]),\n\
                    .output_valid(valid1),\n\
                    .output_encoded(out1),\n\
                    .output_unencoded(out_un[W2-1:0])\n\
                );\n\
                priority_encoder #(\n\
                    .WIDTH(W2),\n\
                    .LSB_PRIORITY(LSB_PRIORITY)\n\
                )\n\
                priority_encoder_inst2 (\n\
                    .input_unencoded({{W1-WIDTH{1\'b0}}, input_unencoded[WIDTH-1:W2]}),\n\
                    .output_valid(valid2),\n\
                    .output_encoded(out2),\n\
                    .output_unencoded(out_un[WIDTH-1:W2])\n\
                );')
        gen_if.EmbeddedCode('       assign output_valid = valid1 | valid2;\n\
                if (LSB_PRIORITY == "LOW") begin\n\
                    assign output_encoded = valid2 ? {1\'b1, out2} : {1\'b0, out1};\n\
                end else begin\n\
                    assign output_encoded = valid1 ? {1\'b0, out1} : {1\'b1, out2};\n\
                end')
        m.EmbeddedCode('assign output_unencoded = 1 << output_encoded;')

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_arbiter(self):
        name = 'arbiter'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        PORTS = m.Parameter('PORTS', 4)
        TYPE = m.Parameter('TYPE', "ROUND_ROBIN")
        BLOCK = m.Parameter('BLOCK', "NONE")
        LSB_PRIORITY = m.Parameter('LSB_PRIORITY', "LOW")
        clk = m.Input('clk')
        rst = m.Input('rst')
        request = m.Input('request', PORTS)
        acknowledge = m.Input('acknowledge', PORTS)
        grant = m.Output('grant', PORTS)
        grant_valid = m.Output('grant_valid')
        grant_encoded = m.Output('grant_encoded', EmbeddedCode('$clog2(PORTS)'))

        grant_reg = m.Reg('grant_reg', PORTS)
        grant_next = m.Reg('grant_next', PORTS)
        grant_valid_reg = m.Reg('grant_valid_reg')
        grant_valid_next = m.Reg('grant_valid_next')
        grant_encoded_reg = m.Reg('grant_encoded_reg', EmbeddedCode('$clog2(PORTS)'))
        grant_encoded_next = m.Reg('grant_encoded_next', EmbeddedCode('$clog2(PORTS)'))

        m.Assign(grant_valid(grant_valid_reg))
        m.Assign(grant(grant_reg))
        m.Assign(grant_encoded(grant_encoded_reg))

        request_valid = m.Wire('request_valid')
        request_index = m.Wire('request_index', EmbeddedCode('$clog2(PORTS)'))
        request_mask = m.Wire('request_mask', PORTS)

        pe = self.create_priority_encoder()
        params = [('WIDTH', PORTS), ('LSB_PRIORITY', LSB_PRIORITY)]
        con = [
            ('input_unencoded', request),
            ('output_valid', request_valid),
            ('output_encoded', request_index),
            ('output_unencoded', request_mask)
        ]
        m.Instance(pe, 'priority_encoder_inst', params, con)
        mask_reg = m.Reg('mask_reg', PORTS)
        mask_next = m.Reg('mask_next', PORTS)
        masked_request_valid = m.Wire('masked_request_valid')
        masked_request_index = m.Wire('masked_request_index', EmbeddedCode('$clog2(PORTS)'))
        masked_request_mask = m.Wire('masked_request_mask', PORTS)
        params = [('WIDTH', PORTS), ('LSB_PRIORITY', LSB_PRIORITY)]
        con = [
            ('input_unencoded', request & mask_reg),
            ('output_valid', masked_request_valid),
            ('output_encoded', masked_request_index),
            ('output_unencoded', masked_request_mask)
        ]
        m.Instance(pe, 'priority_encoder_masked', params, con)

        m.Always()(
            grant_next(0, blk=True),
            grant_valid_next(0, blk=True),
            grant_encoded_next(0, blk=True),
            mask_next(mask_reg, blk=True),
            If(AndList(BLOCK == "REQUEST", grant_reg & request))(
                grant_valid_next(grant_valid_reg, blk=True),
                grant_next(grant_reg, blk=True),
                grant_encoded_next(grant_encoded_reg, blk=True)
            ).Elif(AndList(BLOCK == "ACKNOWLEDGE", grant_valid, Not(grant_reg & acknowledge)))(
                grant_valid_next(grant_valid_reg, blk=True),
                grant_next(grant_reg, blk=True),
                grant_encoded_next(grant_encoded_reg, blk=True)
            ).Elif(request_valid)(
                If(TYPE == "PRIORITY")(
                    grant_valid_next(1, blk=True),
                    grant_next(request_mask, blk=True),
                    grant_encoded_next(request_index, blk=True)
                ).Elif(TYPE == "ROUND_ROBIN")(
                    If(masked_request_valid)(
                        grant_valid_next(1, blk=True),
                        grant_next(masked_request_mask, blk=True),
                        grant_encoded_next(masked_request_index, blk=True),
                        If(LSB_PRIORITY == "LOW")(
                            EmbeddedCode('mask_next = {PORTS{1\'b1}} >> (PORTS - masked_request_index);')
                        ).Else(
                            EmbeddedCode('mask_next = {PORTS{1\'b1}} << (masked_request_index + 1);')
                        )
                    ).Else(
                        grant_valid_next(1, blk=True),
                        grant_next(request_mask, blk=True),
                        grant_encoded_next(request_index, blk=True),
                        If(LSB_PRIORITY == "LOW")(
                            EmbeddedCode('mask_next = {PORTS{1\'b1}} >> (PORTS - request_index);')
                        ).Else(
                            EmbeddedCode('mask_next = {PORTS{1\'b1}} << (request_index + 1);')
                        )
                    )
                )

            )
        )
        m.Always(Posedge(clk))(
            If(rst)(
                grant_reg(0),
                grant_valid_reg(0),
                grant_encoded_reg(0),
                mask_reg(0)
            ).Else(
                grant_reg(grant_next),
                grant_valid_reg(grant_valid_next),
                grant_encoded_reg(grant_encoded_next),
                mask_reg(mask_next)
            )
        )

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_mux(self, n, bits):
        if n < 2:
            raise Exception("Numero minimo de entradas sao 2, encontrado: %d" % n)

        name = 'mux%dx1' % n
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        width = m.Parameter('WIDTH', bits)
        ports_in = []
        for i in range(n):
            ports_in.append(m.Input('in%d' % i, width))

        s_bits = int(math.ceil(math.log(n, 2)))

        s = m.Input('s', s_bits)

        out = m.Output('out', width)
        wr = m.Wire('ins', width, n)
        for i in range(len(ports_in)):
            m.Assign(wr[i](ports_in[i]))

        m.Assign(out(wr[s]))

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_control_arbiter(self, num_units):
        name = 'control_arbiter'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        bits = int(math.ceil(math.log(num_units, 2)))
        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')

        has_data_out = m.Input('has_data_out', num_units)
        has_lst3_data = m.Input('has_lst3_data', num_units)
        gnr_available_write = m.Input('gnr_available_write')

        read_data_en = m.OutputReg('read_data_en', num_units)
        wr_fifo_out = m.OutputReg('wr_fifo_out')
        mux_control = m.OutputReg('mux_control', bits)

        FSM_IDLE = m.Localparam('FSM_IDLE', 0)
        FSM_RD_REQ = m.Localparam('FSM_RD_REQ', 1)
        FSM_WR_REQ = m.Localparam('FSM_WR_REQ', 2)
        fsm_state = m.Reg('fsm_state', 3)

        request = m.Reg('request', num_units)
        grant_index_reg = m.Reg('grant_index_reg', bits)

        grant = m.Wire('grant', num_units)
        grant_index = m.Wire('grant_index', bits)
        grant_valid = m.Wire('grant_valid')

        arbiter = self.create_arbiter()
        params = [('PORTS', num_units), ('TYPE', "ROUND_ROBIN"), ('BLOCK', "NONE"), ('LSB_PRIORITY', "LOW")]
        ports = [('clk', clk), ('rst', rst), ('request', request), ('acknowledge', Int(0, num_units, 10)),
                 ('grant', grant), ('grant_valid', grant_valid), ('grant_encoded', grant_index)]

        m.Instance(arbiter, 'arbiter_inst', params, ports)

        m.Always(Posedge(clk))(
            If(rst)(
                fsm_state(FSM_IDLE),
                request(Int(0, request.width, 10)),
                read_data_en(Int(0, 1, 2)),
                grant_index_reg(Int(0, grant_index.width, 10)),
                wr_fifo_out(Int(0, 1, 2)),
                mux_control(Int(0, mux_control.width, 10)),
            ).Elif(start)(
                request(Int(0, request.width, 10)),
                read_data_en(Int(0, 1, 2)),
                wr_fifo_out(Int(0, 1, 2)),
                mux_control(Int(0, mux_control.width, 10)),
                Case(fsm_state)(
                    When(FSM_IDLE)(
                        If(AndList(Uor(has_data_out), gnr_available_write))(
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
                        wr_fifo_out(Int(1, 1, 2)),
                        mux_control(grant_index_reg),
                        fsm_state(FSM_IDLE)
                    )
                )
            )
        )

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_control_fifo_out(self, data_out_width, num_units):
        name = 'control_fifo_out'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')
        task_done = m.Input('task_done', num_units)
        wr_en = m.Input('wr_en')
        wr_data = m.Input('wr_data', data_out_width)

        gnr_available_write = m.Input('gnr_available_write')
        gnr_done_wr_data = m.Input('gnr_done_wr_data')
        gnr_request_write = m.OutputReg('gnr_request_write')
        gnr_write_data = m.OutputReg('gnr_write_data', 512)
        done = m.OutputReg('done')

        count_empty = m.Reg('count_empty', 3)

        fsm_cs = m.Reg('fms_cs', 2)
        FSM_FIFO_WR = m.Localparam('FSM_FIFO_WR0', 0, 2)
        FSM_DONE = m.Localparam('FSM_DONE', 1, 2)

        m.Always(Posedge(clk))(
            If(rst)(
                fsm_cs(FSM_FIFO_WR),
                gnr_request_write(0),
                done(0),
                count_empty(0),
            ).Elif(start)(
                gnr_request_write(0),
                Case(fsm_cs)(
                    When(FSM_FIFO_WR)(
                        If(wr_en)(
                            gnr_write_data(wr_data),
                            gnr_request_write(1),
                        ).Elif(AndList(Uand(task_done), gnr_done_wr_data))(
                            fsm_cs(FSM_DONE)
                        ),
                    ),
                ),
                When(FSM_DONE)(
                    done(1)
                ),
            )
        )

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_control_data_out(self, num_units, data_out_width):
        name = 'control_data_out'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')

        gnr_done_wr_data = m.Input('gnr_done_wr_data')

        gnr_available_write = m.Input('gnr_available_write')
        gnr_request_write = m.Output('gnr_request_write')
        gnr_write_data = m.Output('gnr_write_data', data_out_width)

        has_data = m.Input('has_data', num_units)
        has_lst3_data = m.Input('has_lst3_data', num_units)
        ports_in = {}
        for p in range(num_units):
            ports_in['din%d' % p] = m.Input('din%d' % p, data_out_width)
        task_done = m.Input('task_done', num_units)
        done = m.Output('done')

        if num_units == 1:
            read_data_en = m.OutputReg('read_data_en', num_units)
        else:
            read_data_en = m.Output('read_data_en', num_units)

        if num_units > 1:
            wr_fifo_out = m.Wire('wr_fifo_out')

            mux_num_bits = int(math.ceil(math.log(num_units, 2)))
            mux_control = m.Wire('mux_control', mux_num_bits)
            mux_data_out = m.Wire('mux_data_out', data_out_width)

            control_arbiter = self.create_control_arbiter(num_units)
            con = [('clk', clk), ('rst', rst), ('start', start), ('has_data_out', has_data),
                   ('has_lst3_data', has_lst3_data), ('gnr_available_write', gnr_available_write),
                   ('read_data_en', read_data_en), ('wr_fifo_out', wr_fifo_out),
                   ('mux_control', mux_control)]
            m.Instance(control_arbiter, 'control_arbiter', control_arbiter.get_params(), con)

            mux_wr_fifo_out = self.create_mux(num_units, data_out_width)
            con = []
            for i in range(num_units):
                con.append(('in%d' % i, ports_in.get('din%d' % i)))
            con.append(('s', mux_control))
            con.append(('out', mux_data_out))
            m.Instance(mux_wr_fifo_out, 'mux_wr_fifo_out', [('WIDTH', data_out_width)], con)

            control_fifo_out = self.create_control_fifo_out(data_out_width, num_units)
            con = [('clk', clk), ('rst', rst), ('start', start), ('task_done', task_done), ('wr_en', wr_fifo_out),
                   ('wr_data', mux_data_out), ('gnr_available_write', gnr_available_write),
                   ('gnr_done_wr_data', gnr_done_wr_data), ('gnr_request_write', gnr_request_write),
                   ('gnr_write_data', gnr_write_data), ('done', done)]
            m.Instance(control_fifo_out, 'control_fifo_out', control_fifo_out.get_params(), con)
        '''else:
            wr_fifo_out = m.Reg("wr_fifo_out")
            flag_pass = m.Reg('flag_pass')
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
                            read_data_en(Int(1, 1, 2))
                        )
                    ),
                    If(read_data_en)(
                        wr_fifo_out(Int(1, 1, 2))
                    )

                )
            )
            control_fifo_out = make_control_fifo_out(data_width, num_units)
            con = [('clk', clk), ('rst', rst), ('start', start), ('num_data_out', num_data_out),
                   ('task_done', task_done),
                   ('wr_en', wr_fifo_out), ('wr_data', ports_in.get('din0')), ('fifoout_full', fifo_out_full),
                   ('fifoout_almostfull', fifo_out_almostfull), ('fifoout_empty', fifo_out_empty),
                   ('wr_fifoout_en', wr_fifo_out_en), ('wr_fifoout_data', wr_fifo_out_data), ('done', done)]

        m.Instance(control_fifo_out, 'control_fifo_out', control_fifo_out.get_params(), con)'''

        return m

    # Código legado
    def create_gnr_harp(self, num_units, functions, fifo_in_size, fifo_out_size):
        name = 'gnr_harp'
        if name in self.cache.keys():
            return self.cache[name]

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

        m = Module(name)
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
        return m
