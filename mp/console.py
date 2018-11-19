from argparse import ArgumentParser

from mp.utils import find_interpreter


if __name__ == '__main__':
    parser = ArgumentParser(prog='mp', usage='%(prog)s [options]')
    parser.add_argument('-d', '--dir-process', help='Run the shell from that directory. (default: current directory)',
                        default='.')
    parser.add_argument('-i', '--interpreter', help='Select the interpreter to run the graph. (default: Python)',
                        default='Python')
    parser.add_argument('--debug', help='Catch the exception and interrupt process. (default: False)',
                        action='store_true')
    parser.add_argument('-c,', '--use-cuda', help='Use the CUDA acceleration driver instead of the CPU. (default: False)',
                        action='store_true')
    args = parser.parse_args()

    interpreter = find_interpreter(args.interpreter)
    cmd = interpreter(dir_process=args.dir_process, use_cuda=args.use_cuda)
    cmd.begin_interactive(debug=args.debug)
