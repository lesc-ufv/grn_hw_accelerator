from math import ceil, log

from veriloggen import *
from veriloggen.types.util import *

from src.hw.utils import initialize_regs  # , bits


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
        output_encoded = m.Output('output_encoded', EmbeddedCode('$clog2(width)'))
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
        grant_encoded = m.Output('grant_encoded', EmbeddedCode('$clog2(ports)'))

        grant_reg = m.Reg('grant_reg', ports)
        grant_next = m.Reg('grant_next', ports)
        grant_valid_reg = m.Reg('grant_valid_reg')
        grant_valid_next = m.Reg('grant_valid_next')
        grant_encoded_reg = m.Reg('grant_encoded_reg', EmbeddedCode('$clog2(ports)'))
        grant_encoded_next = m.Reg('grant_encoded_next', EmbeddedCode('$clog2(ports)'))

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
        masked_request_index = m.Wire('masked_request_index', EmbeddedCode('$clog2(ports)'))
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
            ).Elif(AndList(block == "ACKNOWLEDGE", grant_valid, Not(grant_reg & acknowledge)))(
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
        fifo_almost_full_threshold = m.Parameter('fifo_almost_full_threshold', EmbeddedNumeric('2**fifo_depth_bits - 4'))
        fifo_almost_empty_threshold = m.Parameter('fifo_almost_empty_threshold', 2)

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
                            If(count == EmbeddedNumeric('2**fifo_depth_bits-1'))(
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
            raise Exception("Numero minimo de entradas sao 2, encontrado: %d" % n)

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

    def create_no(self, funcao, debug=False):
        name = 'no_%s' % (funcao.split('=')[0].replace(' ', ''))
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        clk = m.Input('clk')
        start = m.Input('start')
        rst = m.Input('rst')
        reset = m.Input('reset_nos')
        start_s0 = m.Input('start_s0')
        start_s1 = m.Input('start_s1')
        init_state = m.Input('init_state')

        s0 = m.OutputReg('s0', 1)
        s1 = m.OutputReg('s1', 1)
        out_s0 = m.Output(name + '_s0', 1)
        out_s1 = m.Output(name + '_s1', 1)

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

