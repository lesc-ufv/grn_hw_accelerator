import argparse
import os
import sys
import traceback

p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not p in sys.path:
    sys.path.insert(0, p)

from veriloggen import *

from src.hw.grn_accelerator_aws import GrnAccelerator
from src.hw.create_acc_axi_interface import AccAXIInterface
from src.hw.utils import commands_getoutput


def write_file(name, string):
    with open(name, 'w') as fp:
        fp.write(string)
        fp.close()


def create_args():
    parser = argparse.ArgumentParser('create_project -h')
    parser.add_argument('-g', '--grn', help='GRN description file', type=str)
    parser.add_argument('-c', '--copies', help='Number of copies', type=int)
    parser.add_argument('-n', '--name', help='Project name', type=str, default='a.prj')
    parser.add_argument('-o', '--output', help='Project location', type=str, default='.')

    return parser.parse_args()


def create_project(GRN_root, grn_file, copies, name, output_path):
    
    grnacc = GrnAccelerator(copies, grn_file)
    acc_axi = AccAXIInterface(grnacc)

    template_path = GRN_root + '/resources/template.prj'
    cmd = 'cp -r %s  %s/%s' % (template_path, output_path, name)
    commands_getoutput(cmd)

    hw_path = '%s/%s/xilinx_aws_f1/hw/' % (output_path, name)
    sw_path = '%s/%s/xilinx_aws_f1/sw/' % (output_path, name)

    m = acc_axi.create_kernel_top(name)
    m.to_verilog(hw_path + 'src/%s.v' % (name))

    num_channels = '#define NUM_CHANNELS %d'% grnacc.get_num_in()
    num_axis_str = 'NUM_M_AXIS=%d' % grnacc.get_num_in()
    conn_str = acc_axi.get_connectivity_config(name)
    

    write_file(hw_path + 'simulate/num_m_axis.mk', num_axis_str)
    write_file(hw_path + 'synthesis/num_m_axis.mk', num_axis_str)
    write_file(sw_path + 'host/prj_name', name)
    write_file(sw_path + 'host/include/num_channels.h',num_channels)
    write_file(hw_path + 'simulate/prj_name', name)
    write_file(hw_path + 'synthesis/prj_name', name)
    write_file(hw_path + 'simulate/vitis_config.txt', conn_str)
    write_file(hw_path + 'synthesis/vitis_config.txt', conn_str)


def main():
    args = create_args()
    running_path = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    GRN_root = os.getcwd()

    if args.output == '.':
        args.output = running_path

    if args.grn and args.copies:
        args.grn = running_path + '/' + args.grn
        create_project(GRN_root, args.grn, args.copies , args.name, args.output)

        print('Project successfully created in %s/%s' % (args.output, args.name))
    else:
        msg = 'Missing parameters. Run create_project -h to see all parameters needed'

        raise Exception(msg)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        traceback.print_exc()
