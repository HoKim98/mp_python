from argparse import ArgumentParser
from mp import PyTorchInterpreter


if __name__ == '__main__':
    parser = ArgumentParser(prog='mp', usage='%(prog)s [options]')
    parser.add_argument('-d', '--dir-process', help='Run the shell from that directory. (default: parent directory)',
                        default='..')
    args = parser.parse_args()
    cmd = PyTorchInterpreter(dir_process=args.dir_process)
    cmd.begin_interactive(debug=True)
