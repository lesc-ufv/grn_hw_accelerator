import math
from veriloggen import *
from src.hw.utils import initialize_regs


class Components:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.cache = {}

    def create_register_pipeline(self):
        name = 'reg_pipe'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        num_stages = m.Parameter('num_register', 1)
        data_width = m.Parameter('width', 16)

        clk = m.Input('clk')
        en = m.Input('en')
        rst = m.Input('rst')
        data_in = m.Input('in', data_width)
        data_out = m.Output('out', data_width)

        m.EmbeddedCode('(* keep = "true" *)')
        regs = m.Reg('regs', data_width, num_stages)
        i = m.Integer('i')
        m.EmbeddedCode('')
        data_out.assign(regs[num_stages - 1])
        m.Always(Posedge(clk))(
            If(rst)(
                regs[0](0),
            ).Else(
                If(en)(
                    regs[0](data_in),
                    For(i(1), i < num_stages, i.inc())(
                        regs[i](regs[i - 1])
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
        width = m.Parameter('width', 4)
        lsb_priority = m.Parameter('lsb_priority', "LOW")

        input_unencoded = m.Input('input_unencoded', width)
        output_valid = m.Output('output_valid', 1)
        output_encoded = m.Output('output_encoded',
                                  EmbeddedCode('$clog2(width)'))
        output_unencoded = m.Output('output_unencoded', width)

        W1 = m.Localparam('W1', EmbeddedCode('2**$clog2(width)'))
        W2 = m.Localparam('W2', EmbeddedCode('W1/2'))

        gen_if = m.GenerateIf(width == 2, 'if_width')
        gen_if.Assign(output_valid(input_unencoded[0] | input_unencoded[1]))
        gen_if2 = gen_if.GenerateIf(lsb_priority == 'LOW', 'if_low')
        gen_if2.Assign(output_encoded(input_unencoded[1]))
        gen_if2 = gen_if2.Else('else_low')
        gen_if2.EmbeddedCode('assign output_encoded = ~input_unencoded[0];')
        gen_if = gen_if.Else('else_width')
        gen_if.Wire('out1', EmbeddedCode('$clog2(W2)'))
        gen_if.Wire('out2', EmbeddedCode('$clog2(W2)'))
        gen_if.Wire('valid1')
        gen_if.Wire('valid2')
        gen_if.Wire('out_un', width)
        gen_if.EmbeddedCode('priority_encoder #(\n\
                .width(W2),\n\
                .lsb_priority(lsb_priority)\n\
            )\n\
            priority_encoder_inst1 (\n\
                .input_unencoded(input_unencoded[W2-1:0]),\n\
                .output_valid(valid1),\n\
                .output_encoded(out1),\n\
                .output_unencoded(out_un[W2-1:0])\n\
            );\n\
            priority_encoder #(\n\
                .width(W2),\n\
                .lsb_priority(lsb_priority)\n\
            )\n\
            priority_encoder_inst2 (\n\
                .input_unencoded({{W1-width{1\'b0}}, input_unencoded[width-1:W2]}),\n\
                .output_valid(valid2),\n\
                .output_encoded(out2),\n\
                .output_unencoded(out_un[width-1:W2])\n\
            );')
        gen_if.EmbeddedCode('       assign output_valid = valid1 | valid2;\n\
            if (lsb_priority == "LOW") begin\n\
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
        ports = m.Parameter('ports', 4)
        type = m.Parameter('type', "ROUND_ROBIN")
        block = m.Parameter('block', "NONE")
        lsb_priority = m.Parameter('lsb_priority', "LOW")

        clk = m.Input('clk')
        rst = m.Input('rst')
        request = m.Input('request', ports)
        acknowledge = m.Input('acknowledge', ports)
        grant = m.Output('grant', ports)
        grant_valid = m.Output('grant_valid')
        grant_encoded = m.Output('grant_encoded',
                                 EmbeddedCode('$clog2(ports)'))

        grant_reg = m.Reg('grant_reg', ports)
        grant_next = m.Reg('grant_next', ports)
        grant_valid_reg = m.Reg('grant_valid_reg')
        grant_valid_next = m.Reg('grant_valid_next')
        grant_encoded_reg = m.Reg('grant_encoded_reg',
                                  EmbeddedCode('$clog2(ports)'))
        grant_encoded_next = m.Reg('grant_encoded_next',
                                   EmbeddedCode('$clog2(ports)'))

        m.Assign(grant_valid(grant_valid_reg))
        m.Assign(grant(grant_reg))
        m.Assign(grant_encoded(grant_encoded_reg))

        request_valid = m.Wire('request_valid')
        request_index = m.Wire('request_index', EmbeddedCode('$clog2(ports)'))
        request_mask = m.Wire('request_mask', ports)

        pe = self.make_priority_encoder()
        params = [('WIDTH', ports), ('lsb_priority', lsb_priority)]
        con = [
            ('input_unencoded', request),
            ('output_valid', request_valid),
            ('output_encoded', request_index),
            ('output_unencoded', request_mask)
        ]
        m.Instance(pe, 'priority_encoder_inst', params, con)
        mask_reg = m.Reg('mask_reg', ports)
        mask_next = m.Reg('mask_next', ports)
        masked_request_valid = m.Wire('masked_request_valid')
        masked_request_index = m.Wire('masked_request_index',
                                      EmbeddedCode('$clog2(ports)'))
        masked_request_mask = m.Wire('masked_request_mask', ports)
        params = [('WIDTH', ports), ('lsb_priority', lsb_priority)]
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
            If(AndList(block == "REQUEST", grant_reg & request))(
                grant_valid_next(grant_valid_reg, blk=True),
                grant_next(grant_reg, blk=True),
                grant_encoded_next(grant_encoded_reg, blk=True)
            ).Elif(AndList(block == "ACKNOWLEDGE", grant_valid,
                           Not(grant_reg & acknowledge)))(
                grant_valid_next(grant_valid_reg, blk=True),
                grant_next(grant_reg, blk=True),
                grant_encoded_next(grant_encoded_reg, blk=True)
            ).Elif(request_valid)(
                If(type == "PRIORITY")(
                    grant_valid_next(1, blk=True),
                    grant_next(request_mask, blk=True),
                    grant_encoded_next(request_index, blk=True)
                ).Elif(type == "ROUND_ROBIN")(
                    If(masked_request_valid)(
                        grant_valid_next(1, blk=True),
                        grant_next(masked_request_mask, blk=True),
                        grant_encoded_next(masked_request_index, blk=True),
                        If(lsb_priority == "LOW")(
                            EmbeddedCode('mask_next = {ports{1\'b1}} >> (ports - masked_request_index);')
                        ).Else(
                            EmbeddedCode('mask_next = {ports{1\'b1}} << (masked_request_index + 1);')
                        )
                    ).Else(
                        grant_valid_next(1, blk=True),
                        grant_next(request_mask, blk=True),
                        grant_encoded_next(request_index, blk=True),
                        If(lsb_priority == "LOW")(
                            EmbeddedCode('mask_next = {ports{1\'b1}} >> (ports - request_index);')
                        ).Else(
                            EmbeddedCode('mask_next = {ports{1\'b1}} << (request_index + 1);')
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

    def create_control_arbiter(self, num_units):
        name = 'control_arbiter'
        if name in self.cache.keys():
            return self.cache[name]

        bits = int(math.ceil(math.log(num_units, 2)))

        m = Module(name)
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
            request = m.Reg('request', num_units)
            grant_index_reg = m.Reg('grant_index_reg', bits)

            grant = m.Wire('grant', num_units)
            grant_index = m.Wire('grant_index', bits)
            grant_valid = m.Wire('grant_valid')

            arbiter = self.make_arbiter()
            params = [('PORTS', num_units), ('TYPE', "ROUND_ROBIN"),
                      ('BLOCK', "NONE"), ('LSB_PRIORITY', "LOW")]
            ports = [('clk', clk), ('rst', rst), ('request', request),
                     ('acknowledge', Int(0, num_units, 10)),
                     ('grant', grant),
                     ('grant_valid', grant_valid),
                     ('grant_encoded', grant_index)]

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
                            If(AndList(has_data_out !=
                                       Int(0, has_data_out.width, 10),
                                       Not(fifo_out_full)))(
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
                    If(AndList(has_data_out != Int(0, num_units, 10),
                               ~fifo_out_full))(
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

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_fifo(self):
        name = 'fifo'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        fifo_width = m.Parameter('fifo_width', 32)
        fifo_depth_bits = m.Parameter('fifo_depth_bits', 8)
        fifo_almost_full_threshold = \
            m.Parameter('fifo_almost_full_threshold',
                        EmbeddedNumeric('2**fifo_depth_bits - 4'))
        fifo_almost_empty_threshold = \
            m.Parameter('fifo_almost_empty_threshold', 2)

        clk = m.Input('clk')
        rst = m.Input('rst')
        we = m.Input('we')
        din = m.Input('din', fifo_width)
        re = m.Input('re')
        dout = m.OutputReg('dout', fifo_width)
        empty = m.OutputReg('empty')
        almostempty = m.OutputReg('almostempty')
        full = m.OutputReg('full')
        almostfull = m.OutputReg('almostfull')

        rp = m.Reg('rp', fifo_depth_bits)
        wp = m.Reg('wp', fifo_depth_bits)
        count = m.Reg('count', fifo_depth_bits)
        mem = m.Reg('mem', fifo_width, EmbeddedNumeric('2**fifo_depth_bits'))

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
                            If(count == (fifo_almost_empty_threshold - 1))(
                                almostempty(Int(0, 1, 2))
                            ),
                            If(count ==
                               EmbeddedNumeric('2**fifo_depth_bits-1'))(
                                full(Int(1, 1, 2))
                            ),
                            If(count == (fifo_almost_full_threshold - 1))(
                                almostfull(Int(1, 1, 2))
                            )
                        )

                    ),
                    When(Int(1, 2, 2))(
                        If(~empty)(
                            rp.inc(),
                            count(count - 1),
                            full(Int(0, 1, 2)),
                            If(count == fifo_almost_full_threshold)(
                                almostfull(Int(0, 1, 2))
                            ),
                            If(count == 1)(
                                empty(Int(1, 1, 2))
                            ),
                            If(count == fifo_almost_empty_threshold)(
                                almostempty(Int(1, 1, 2))
                            )

                        )
                    ),
                    When()(

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

    def create_mux(self, n, bits):
        name = 'mux%dx1' % n
        if name in self.cache.keys():
            return self.cache[name]

        if n < 2:
            raise Exception("Numero minimo de entradas sao 2, encontrado: %d"
                            % n)

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

    def create_gnr_no(self, funcao, debug=False):
        sufix = funcao.split('=')[0].replace(' ', '')
        name = 'no_%s' % sufix
        if sufix in self.cache.keys():
            return self.cache[sufix]

        m = Module(name)
        clk = m.Input('clk')
        start = m.Input('start')
        rst = m.Input('rst')
        rst_nos = m.Input('rst_nos')
        start_s0 = m.Input('start_s0')
        start_s1 = m.Input('start_s1')
        init_state = m.Input('init_state')

        ops = {'and': ' & ', 'or': ' | ', 'not': ' ~ ', 'xor': ' ^ ',
               'nor': ' ~| ', 'nand': ' ~& ', 'xnor': ' ~^ '}

        funcao_orig = funcao
        funcao = re.sub(u'[()]', '', funcao)
        funcao = funcao.split("=")[1].split(" ")
        ops1 = ops.keys()
        port_names = []
        for port in funcao:
            if port not in ops1 and port != "":
                if port != sufix and port not in port_names:
                    m.Input(port + '_s0', 1)
                    m.Input(port + '_s1', 1)
                    port_names.append(port)

        s0 = m.OutputReg('s0', 1)
        s1 = m.OutputReg('s1', 1)
        out_s0 = m.Output(sufix + '_s0', 1)
        out_s1 = m.Output(sufix + '_s1', 1)

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
                funcao_orig_s0 = re.sub(token, ' ' + p + '_s0 ',
                                        funcao_orig_s0)
                funcao_orig_s1 = re.sub(token, ' ' + p + '_s1 ',
                                        funcao_orig_s1)

        token = ' ' + sufix + ' '
        funcao_orig_s0 = re.sub(token, ' s0 ', funcao_orig_s0)
        funcao_orig_s1 = re.sub(token, ' s1 ', funcao_orig_s1)

        funcao_orig_s0 = funcao_orig_s0.split('=')[1]
        funcao_orig_s1 = funcao_orig_s1.split('=')[1]

        passs = m.Reg('pass')

        if debug:
            clk_count = m.Reg("clk_count", 64)

            m.Always(Posedge(clk))(
                If(rst_nos)(
                    clk_count(0),
                ).Elif(start)(
                    clk_count.inc()
                )
            )

            '''m.Always(s0)(
                Display("%d: NO %s s0: %d s0 next: %d", clk_count, sufix, s0,
                 EmbeddedNumeric(funcao_orig_s0))
            )
            m.Always(s1)(
                Display("%d: NO %s s1: %d s1 next: %d", clk_count, sufix, s1,
                 EmbeddedNumeric(funcao_orig_s1))
            )'''

        m.Always(Posedge(clk))(
            If(rst_nos)(
                s0(init_state),
                passs(1),
                # Display("%d: RESET NO s0 %s %d", clk_count, sufix,init_state)
            ).Elif(start_s0)(
                If(passs)(
                    s0(EmbeddedNumeric(funcao_orig_s0)),
                    # Display("%d: NO %s s0: %d s0 next: %d",clk_count, sufix,
                    # s0, EmbeddedNumeric(funcaoB_s0))
                ),
                passs(~passs)
            )
        )
        m.Always(Posedge(clk))(
            If(rst_nos)(
                s1(init_state)
            ).Elif(start_s1)(
                s1(EmbeddedNumeric(funcao_orig_s1))
                # Display("%d: NO %s s1: %d s1 next: %d",clk_count ,sufix, s1,
                # EmbeddedNumeric(funcaoB_s1))
            )
        )
        m.Assign(out_s0(s0))
        m.Assign(out_s1(s1))

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_gnr_control(self, functions, debug=False):
        name = "gnr_control"
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        data_width = 29
        width = len(functions)

        ID = m.Parameter('ID', 0)

        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')

        fifo_out_full = m.Input('fifo_out_full')
        fifo_in_empty = m.Input('fifo_in_empty')
        fifo_data_in = m.Input('fifo_data_in', 2 * width)
        end_data_in = m.Input('end_data_in')
        fifo_in_re = m.OutputReg('fifo_in_re')

        fifo_out_we = m.OutputReg('fifo_out_we')
        fifo_out_empty = m.Input('fifo_out_empty')
        data_out = m.OutputReg('data_out', (data_width + data_width + width))

        done = m.OutputReg('done')

        s0 = m.Wire('s0', width)
        s1 = m.Wire('s1', width)
        start_s0 = m.Reg('start_s0')
        start_s1 = m.Reg('start_s1')
        rst_nos = m.Reg('rst_nos')
        init_state_out = m.Reg('init_state', width)

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
        flag_rd = m.Reg('flag_rd')
        flag_wr = m.Reg('flag_wr')
        pass_cycle_attractor = m.Reg("pass_cycle_attractor")

        fsm_state = m.Reg('fsm_state', 3)
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
                rst_nos(Int(0, 1, 2)),
                data_out(Int(0, data_out.width, 10)),
                fsm_state(IDLE),
                pass_cycle_attractor(Int(1, 1, 2))
            ).Elif(start)(
                fifo_out_we(Int(0, 1, 2)),
                rst_nos(Int(0, 1, 2)),
                reset_counts(Int(0, 1, 2)),
                fifo_in_re(Int(0, 1, 2)),
                Case(fsm_state)(
                    When(IDLE)(
                        If(~fifo_in_empty)(
                            fifo_in_re(Int(1, 1, 2)),
                            flag_rd(Int(0, 1, 2)),
                            fsm_state(GET_STATE)
                        ).Elif(end_data_in)(
                            fsm_state(DONE)
                        )
                    ),
                    When(GET_STATE)(
                        If(flag_rd)(
                            init_state_out(fifo_data_in[:width]),
                            end_state_reg(fifo_data_in[width:]),
                            flag_rd(Int(0, 1, 2)),
                            # Display("%d: ID: %d SET_STATE %d / %d", clk_count, ID, fifo_data_in[:width],
                            # fifo_data_in[width:]),
                            fsm_state(RESET_NOS)
                        ).Else(
                            flag_rd(Int(1, 1, 2))
                        )
                    ),
                    When(RESET_NOS)(
                        # Display("%d: ID: %d SET_STATE %d / %d", clk_count, ID, init_state_out, end_state_reg),
                        rst_nos(Int(1, 1, 2)),
                        reset_counts(Int(1, 1, 2)),
                        fsm_state(START_NOS),
                    ),
                    When(START_NOS)(
                        start_s0(Int(1, 1, 2)),
                        start_s1(Int(1, 1, 2)),
                        pass_cycle_attractor(Int(1, 1, 2)),
                        fsm_state(FIND_ATTRACTOR),
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
                                fsm_state(CALC_PERIOD_ATTRACTOR),
                                #  Display("%d: FIND_ATTRACTOR -> CALC_PERIOD_ATTRACTOR: %x %x", clk_count, s0, s1)

                            ).Else(
                                start_count_transient(Int(1, 1, 2)),
                                fsm_state(FIND_ATTRACTOR),
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
                            fsm_state(FIND_NEXT_ATTRACTOR),
                            # Display("%d: CALC_PERIOD_ATTRACTOR -> FIND_NEXT_ATTRACTOR %x %x %d", clk_count, state_net, s1,
                            #      period)
                        ).Else(
                            fsm_state(CALC_PERIOD_ATTRACTOR),
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
                                fsm_state(RESET_NOS),
                                #    Display("%d: ID: %d FIND_NEXT_ATTRACTOR%d", clk_count, ID, init_state_out + 1)
                            ).Else(
                                fsm_state(DONE),
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
                            fsm_state(DONE)
                        ).Else(
                            fifo_in_re(Int(1, 1, 2)),
                            flag_rd(Int(0, 1, 2)),
                            init_state_out(Int(0, init_state_out.width, 10)),
                            fsm_state(GET_STATE)
                        )

                    )
                )

            )
        )

        m.Always(Posedge(clk))(
            If(reset_counts)(
                period_count(Int(0, period.width, 10)),
                transient_count(Int(0, transient_count.width, 10)),
                pass_cycle(Int(1, 1, 2))
            ).Else(
                If(start_count_period)(
                    period_count(period_count + Int(1, period_count.width, 10))
                ),
                If(start_count_transient)(
                    transient_count(transient_count + Cat(Int(0,transient.width - 1,2), pass_cycle))
                ),
                pass_cycle(~pass_cycle),
            )
        )

        graph = self.create_gnr_graph(functions)
        m.Instance(graph, graph.name, graph.get_params(), graph.get_ports())

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_gnr_graph(self, functions):
        name = 'gnr_graph'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        width = len(functions)
        m.Input('clk')
        m.Input('rst')
        m.Input('start')
        m.Input('rst_nos')
        m.Input('start_s0')
        m.Input('start_s1')
        m.Input('init_state', width)
        m.Output('s0', width)
        m.Output('s1', width)

        for f in functions:
            wire = f.split('=')[0].replace(' ', '')
            m.Wire(wire + '_s0')
            m.Wire(wire + '_s1')

        components = Components()
        i = 0
        ports_graph_genes = m.get_ports()
        wires_graph_genes = m.get_vars()
        for f in functions:
            no = components.create_gnr_no(f)
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
