from argparse import ArgumentParser
from getpass import getpass
from mp import RemoteInterpreter

from paramiko.ssh_exception import AuthenticationException


if __name__ == '__main__':
    parser = ArgumentParser(prog='mp', usage='%(prog)s [hostname] [user] [-p port] [-d dir_process] [-i interpreter]')
    parser.add_argument('hostname')
    parser.add_argument('user')
    parser.add_argument('-p', '--port', default=22)
    parser.add_argument('-d', '--dir-process', default='.')
    parser.add_argument('-i', '--interpreter', default='python')
    args = parser.parse_args()

    try:
        sess = RemoteInterpreter(args.dir_process)
        sess.connect(args.hostname, args.user, getpass(), args.port)
        sess.session(python=args.interpreter)
        sess.begin_interactive()
    # auth failed
    except AuthenticationException:
        print('mp: Authentication failure')
    # interrupt
    except KeyboardInterrupt:
        print()
    except EOFError:
        print()
