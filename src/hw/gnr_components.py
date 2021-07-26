import math
from veriloggen import *
from src.hw.utils import initialize_regs


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

    def create_control_fifo_data_in(self,num_units, width_data_in):
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

        initialize_regs(m)
        self.cache[name] = m
        return m



    def create_regulator_network(self, num_units, functions, fifo_in_size, fifo_out_size):
        name = 'regulator_network'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        data_width = 29
        ID = m.Parameter('ID', 0)
        id_width = int(math.ceil(math.log(num_units, 2))) + 1
        width_data_in = 2 * len(functions) + id_width
        width = len(functions)
        fifo_in_depth_bits = int(math.ceil(math.log(fifo_in_size, 2)))
        fifo_out_depth_bits = int(math.ceil(math.log(fifo_out_size, 2)))

        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')
        data_in_valid = m.Input('data_in_valid')
        data_in = m.Input('data_in', width_data_in)  # (ID + BEGIN + END)
        end_data_in = m.Input('end_data_in')
        read_data_en = m.Input('read_data_en')
        has_data_out = m.Output('has_data_out')
        has_lst3_data_out = m.Output('has_lst3_data_out')
        data_out = m.Output('data_out', (data_width + data_width + width))
        task_done = m.Output('task_done')

        s0 = m.Wire('s0', width)
        s1 = m.Wire('s1', width)
        start_s0 = m.Wire('start_s0')
        start_s1 = m.Wire('start_s1')
        reset_nos = m.Wire('reset_nos')
        init_state = m.Wire('init_state', width)

        fifo_out_we = m.Wire('fifo_out_we')
        fifo_out_data_in = m.Wire('fifo_out_data_in', (data_width + data_width + width))
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

        control_fifo_data_in = self.create_control_fifo_data_in(num_units, width_data_in)
        con = [('clk', clk), ('rst', rst), ('start', start), ('data_in_valid', data_in_valid), ('data_in', data_in),
               ('fifo_in_full', fifo_in_full), ('fifo_in_amostfull', fifo_in_full_almostfull),
               ('fifo_in_we', fifo_in_we),
               ('fifo_in_data', fifo_in_data_in)]
        param = [('ID', ID)]

        m.Instance(control_fifo_data_in, 'control_fifo_data_in_', param, con)

        fifo = make_fifo()
        con = [('clk', clk), ('rst', rst), ('we', fifo_in_we), ('din', fifo_in_data_in),
               ('re', fifo_in_re), ('dout', fifo_in_data_out), ('empty', fifo_in_empty),
               ('almostempty', fifo_in_almostempty), ('full', fifo_in_full), ('almostfull', fifo_in_full_almostfull)]

        param = [('FIFO_WIDTH', width_data_in - id_width), ('FIFO_DEPTH_BITS', fifo_in_depth_bits),
                 ('FIFO_ALMOSTFULL_THRESHOLD', fifo_in_size - 2),
                 ('FIFO_ALMOSTEMPTY_THRESHOLD', 2)]

        m.Instance(fifo, 'fifo_in', param, con)

        con = [('clk', clk), ('rst', rst), ('we', fifo_out_we), ('din', fifo_out_data_in),
               ('re', read_data_en), ('dout', data_out), ('empty', fifo_out_empty),
               ('almostempty', has_lst3_data_out), ('full', fifo_out_full), ('almostfull', fifo_out_full_almostfull)]

        param = [('FIFO_WIDTH', (data_width + data_width + width)),
                 ('FIFO_DEPTH_BITS', fifo_out_depth_bits),
                 ('FIFO_ALMOSTFULL_THRESHOLD', fifo_out_size - 2),
                 ('FIFO_ALMOSTEMPTY_THRESHOLD', 2)]

        m.Instance(fifo, 'fifo_out', param, con)

        control = make_control_gnr(len(functions))
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
