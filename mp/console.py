from argparse import ArgumentParser
from mp import PythonInterpreter


if __name__ == '__main__':
    parser = ArgumentParser(prog='mp', usage='%(prog)s [options]')
    parser.add_argument('-d', '--dir-process', help='Run the shell from that directory.', default='.')
    parser.add_argument('--debug', help='Catch the exception and interrupt process.', action='store_true')
    args = parser.parse_args()
    cmd = PythonInterpreter(dir_process=args.dir_process)
    cmd.begin_interactive(debug=args.debug)
