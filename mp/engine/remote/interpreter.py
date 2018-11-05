from queue import Queue
from time import sleep
from threading import Thread

import paramiko

from mp.utils import interactive as _interactive


class Packet:
    def __init__(self, name: str, msg: list):
        self.name = name
        self.msg = msg

    def __repr__(self):
        return '@ %s' % '\n'.join([self.name] + self.msg)


class RemoteInterpreter:

    PROMPT = b'@ '
    # PROMPT = b'>>> '

    PRE_COMMAND = ''

    def __init__(self, dir_process: str = '.'):
        self._dir_process = dir_process
        self._dir_process_remote = None

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.q_in = Queue()
        self.q_out = Queue()

        self.echo = False

    # Connect to SSH
    def connect(self, hostname: str, username: str, password, port: int = paramiko.config.SSH_PORT):
        self.ssh.connect(hostname, port=port, username=username, password=password)

    # Open Python Session
    def session(self, python: str = 'python', pre_command: str = PRE_COMMAND):
        self.session = self.ssh.get_transport().open_session()
        self.session.get_pty()
        self.session.exec_command(pre_command + '%s -m mp.console --dir-process %s' % (python, self.dir_process))
        self.stdIn = self.session.makefile('wb', -1)

        t = Thread(target=self._loop_receive, args=())
        t.daemon = True
        t.start()

    # Command to python
    def command(self, msg: str):
        self.stdIn.write('%s\n' % msg)
        self.stdIn.flush()

    def begin_interactive(self, debug=False):
        _interactive(self, debug=debug)

    # Command to session
    def sess_command(self, token: int):
        self.q_in.put(token)
        self.q_in.task_done()

    def __call__(self, msg: str):
        self.command(msg)
        out = self.q_out.get()
        out = '\n'.join(out.msg)
        if len(out) > 0:
            print(out)

    @property
    def dir_process(self) -> str:
        if self._dir_process_remote is not None:
            return self._dir_process_remote
        if self.ssh is None:
            return self._dir_process
        stdout = self.ssh.exec_command('cd %s; pwd' % self._dir_process)[1]
        stdout.channel.recv_exit_status()
        lines = stdout.readlines()
        pwd = lines[0].rstrip()
        self._dir_process_remote = pwd
        return pwd

    # Read from python
    def _loop_receive(self, interval=0.001):
        stdout = b''
        while True:
            # read
            stdout += self.session.recv(4096)
            # final prompt
            while True:
                head = stdout.find(self.PROMPT)
                tail = stdout.find(self.PROMPT, head+1)
                if head >= 0 and tail >= 0:
                    msg = stdout[head+len(self.PROMPT):tail].decode().split('\r\n')
                    msg = Packet(msg[0], msg[1:-1])
                    self.q_out.put(msg)
                    # echo
                    if self.echo:
                        print(msg)
                    stdout = stdout[tail:]
                    continue
                # wait
                sleep(interval)
                break
            # process commands
            if not self.q_in.empty():
                break

    # Close remote python.
    def __del__(self):
        if self.q_in is not None:
            self.sess_command(0)
        if self.ssh is not None:
            self.ssh.close()
            del self.ssh
