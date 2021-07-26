import re


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
