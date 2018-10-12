import argparse

from mp import PythonInterpreter


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir-process', help='Run the shell from that directory.',
                        default='.', action='store_true')
    args = parser.parse_args()
    cmd = PythonInterpreter(dir_process=args.dir_process)
    cmd.begin_interactive()
