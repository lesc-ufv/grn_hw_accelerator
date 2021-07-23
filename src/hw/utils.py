import re
from veriloggen import *


def readFile(path):
    functions = []
    file = open(path).read()
    file = file.lower()
    file = re.sub('[=]', ' = ', file)
    file = re.sub('[(]', ' ( ', file)
    file = re.sub('[)]', ' ) ', file)
    for f in file.split('\n'):
        if f != '':
            f = re.sub('[-*+%&^><!,.;:/]', '', f)
            f = ' ' + f + ' '
            ff = re.sub('  ', ' ', f)
            while f != ff:
                f = ff
                ff = re.sub('  ', ' ', f)
            functions.append(f)
    return functions


def initialize_regs(module, values=None):
    regs = []
    if values is None:
        values = {}
    flag = False
    for r in module.get_vars().items():
        if module.is_reg(r[0]):
            regs.append(r)
            if r[1].dims:
                flag = True

    if len(regs) > 0:
        if flag:
            i = module.Integer('i_initial')
        s = module.Initial()
        for r in regs:
            if values:
                if r[0] in values.keys():
                    value = values[r[0]]
                else:
                    value = 0
            else:
                value = 0
            if r[1].dims:
                genfor = For(i(0), i < r[1].dims[0], i.inc())(
                    r[1][i](value)
                )
                s.add(genfor)
            else:
                s.add(r[1](value))
