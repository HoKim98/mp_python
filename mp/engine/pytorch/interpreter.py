from mp.core import Interpreter as _Interpreter
from mp.engine.pytorch.device import Device
from mp.engine.pytorch.plan import Plan as _Plan

import os


class Interpreter(_Interpreter):
    HEADER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'builtins', 'builtins.mp')

    def __init__(self, dir_process: str = './', use_cuda: bool = False):
        Device(use_cuda)
        super().__init__(dir_process, _Plan, self.HEADER_FILE)
