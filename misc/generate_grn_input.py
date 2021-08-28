import argparse
import os
import sys
import traceback

from math import ceil

def create_args():
    parser = argparse.ArgumentParser('create_grn_input -h')
    parser.add_argument('-s', '--number', help='Number of states', type=str)
    parser.add_argument('-n', '--num_nos', help='Number of nodes', type=int)
    parser.add_argument('-c', '--copies', help='Number of copies', type=str)
    parser.add_argument('-o', '--output', help='Output file', type=str, default='.')

    return parser.parse_args()

def state(val,size):
    return format(val,"0%dx"%size)

def create_output(num_states,num_nos,num_copies,output):
    num_states = int(eval(num_states))
    num_copies = int(eval(num_copies))
    num_states = min(2**num_nos,num_states)
    
    l = int(ceil(num_nos/8))*2
    state_per_copie = int(num_states/num_copies)
    state_rest = int(num_states%num_copies)
    init = 0
    states = [(0,0,0) for _ in range(num_copies)]
    for c in range(num_copies):
        if state_rest > 0:
            states[c] = (init,init+state_per_copie,state_per_copie+1)
            init += state_per_copie+1
            state_rest -= 1
        else:
            states[c] = (init,init+state_per_copie-1,state_per_copie)
            init += state_per_copie

    with open(output,'w') as f:
        for c in range(num_copies):
            i,e,s = states[c]
            f.write("%d,%s,%s,%d\n"%(c,state(i,l),state(e,l),s))
        f.close()



def main():
    args = create_args()
    running_path = os.getcwd()

    if args.output == '.':
        args.output = running_path

    if args.number and args.num_nos and args.copies and args.output:
        create_output(args.number,args.num_nos, args.copies, args.output)
    else:
        msg = 'Missing parameters. Run create_grn_input -h to see all parameters needed'
        raise Exception(msg)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        traceback.print_exc()
