import argparse
import os
import sys
import traceback

from math import ceil

def create_args():
    parser = argparse.ArgumentParser('extract_grn_properties -h')
    parser.add_argument('-g', '--grn', help='GRN model file', type=str)

    return parser.parse_args()


def extract(grn_file):
    operators = ['and', 'or', 'not', 'xor']
    lines = []
    functions = []
    with open(grn_file,'r') as f:
        lines = f.read().split('\n')
        f.close()

    for l in lines:
        l = l.replace('(',' ')
        l = l.replace(')',' ')
        l = "".join([s + ' ' if s else '' for s in l.split(' ')])
        l = l.strip()
        if len(l) > 0:
            functions.append(l)

    nodes = len(functions)
    edges = 0
    ops = 0
    for f in functions:
        terms = f.split('=')
        if len(terms) > 1:
            terms = terms[1].strip().split(' ')
            for t in terms:
                if t in operators:
                    ops += 1
                else:
                    edges += 1

    print("%s,%d,%d,%d"%(grn_file,nodes,edges,ops))

	
	
	

def main():
    args = create_args()

    if args.grn:
        extract(args.grn)
    else:
        msg = 'Missing parameters. Run extract_grn_properties -h to see all parameters needed'
        raise Exception(msg)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        traceback.print_exc()
