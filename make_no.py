import re

from veriloggen import *


def make_no(funcao, debug = False):
    name = funcao.split('=')[0].replace(' ', '')
    m = Module('no_%s' % name)
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
        token = ' '+op+' '
        if token in funcao_orig:
            op2 = ops.get(op)
            funcao_orig = re.sub(token, op2, funcao_orig)

    funcao_orig_s0 = funcao_orig
    funcao_orig_s1 = funcao_orig

    for p in port_names:
        token = ' '+p+' '
        if token in funcao_orig:
            funcao_orig_s0 = re.sub(token, ' '+p + '_s0 ', funcao_orig_s0)
            funcao_orig_s1 = re.sub(token, ' '+p + '_s1 ', funcao_orig_s1)

    token = ' '+name+' '
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
            s0(Int(0,s0.width,10)),
            passs(Int(0,1,2))
        ).Elif(reset)(
            s0(init_state),
            passs(1),
            #Display("%d: RESET NO s0 %s %d", clk_count, name, init_state)
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
            s1(Int(0,s1.width,10))
        ).Elif(reset)(
            s1(init_state)
        ).Elif(start_s1)(
            s1(EmbeddedNumeric(funcao_orig_s1))
            # Display("%d: NO %s s1: %d s1 next: %d",clk_count ,name, s1, EmbeddedNumeric(funcaoB_s1))
        )
    )
    m.Assign(out_s0(s0))
    m.Assign(out_s1(s1))
    return m
