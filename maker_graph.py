from veriloggen import *

from make_no import make_no


def maker_graph(functions):
    m = Module('network_graph')
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
        no = make_no(f)
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

    return m
