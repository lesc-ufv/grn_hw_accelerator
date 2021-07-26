from __future__ import absolute_import
from __future__ import print_function

import math

from veriloggen import *


def make_mux(n, bits):
    if n < 2:
        raise Exception("Numero minimo de entradas sao 2, encontrado: %d" % n)

    m = Module('mux%dx1' % n)
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
    return m
