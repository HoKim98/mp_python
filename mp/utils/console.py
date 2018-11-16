import cmd

from mp.core.error import BaseError
from mp.utils.environment import is_linux, is_windows
from mp.version import __version__


class _Colors:
    if is_windows():
        HEADER = ''
        OKBLUE = ''
        OKGREEN = ''
        WARNING = ''
        FAIL = ''
        ENDC = ''
        BOLD = ''
        UNDERLINE = ''
    else:
    #elif is_linux():
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'


class _Interactive(cmd.Cmd):

    def __init__(self, interpreter, debug: bool):
        super().__init__()
        self.debug = debug
        self.dir_process = interpreter.dir_process
        self.interpreter = interpreter
        self._set_intro()
        self._set_prompt()

    def _set_intro(self):
        intro  = '----------------------------------------------\n'
        intro += '   Machine Pseudo-Code                        \n'
        intro += '                           v.%s\n' % __version__
        intro += '----------------------------------------------'
        self.intro = intro

    def _set_prompt(self):
        self.prompt = _Colors.OKGREEN + '[%s]' % self.dir_process + _Colors.ENDC + ':@ '

    def default(self, line):
        try:
            self.interpreter(line)
        except BaseError as e:
            if self.debug:
                raise e
            print(_Colors.FAIL + e.message)
        return False

    def precmd(self, line):
        if line == ':q':
            line = 'exit'
        if line == 'EOF':
            line = ''
            print()
        return line

    def postcmd(self, stop, line):
        self._set_prompt()
        return stop

    def do_exit(self, *arg):
        """Escape from here."""
        return self.close()

    def close(self):
        return True


def interactive(self, verbose=True, debug=False):
    v_cmd = _Interactive(self, debug)
    if not verbose:
        v_cmd.intro = ''
    try:
        v_cmd.cmdloop()
    except KeyboardInterrupt:
        print('exit')
