import os

from core.error import BaseError


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def interactive(self, verbose=False, debug=False):
    def print_verbose(*args, **kwargs):
        if verbose:
            print(*args, **kwargs)

    dir_root = os.path.abspath(self.dir_process)
    print_verbose('----------------------------------------------')
    print_verbose('   Machine Pseudo-Code                        ')
    print_verbose('                           v.%s' % self.VERSION)
    print_verbose('----------------------------------------------')
    while True:
        try:
            message = input(Colors.OKGREEN + '[%s]' % dir_root + Colors.ENDC + ':@ ')
            if message == ':q':
                break
            self(message)
        except BaseError as e:
            if debug:
                raise e
            print(Colors.FAIL + e.message)
        except KeyboardInterrupt:
            print()
            break
        except EOFError:
            print()
    print_verbose('Closing...')
