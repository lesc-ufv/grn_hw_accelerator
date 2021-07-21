import argparse
import os
import sys
import traceback

p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(p)
if p not in sys.path:
    sys.path.insert(0, p)


def create_args():
    parser = argparse.ArgumentParser('create_project -h')
    parser.add_argument('-i', '--input', help='GNR expressions file', type=str)
    parser.add_argument('-n', '--name', help='Project name', type=str,
                        default='a.prj')
    parser.add_argument('-o', '--output', help='Project location', type=str,
                        default='.')
    return parser.parse_args()


def main():
    args = create_args()
    running_path = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    gnr_hw_acc_root = os.getcwd() + '/../'

    if args.output == '.':
        args.output = running_path

    if args.input:

        #args.input = running_path + '/' + args.input

        #CREATE PROJECT

        # create_project(hpcgra_root, args.json, args.name, args.output)

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
