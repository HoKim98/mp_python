from core import Interpreter as _Interpreter
from engine.python.plan import Plan as _Plan


class Interpreter(_Interpreter):
    def __init__(self, dir_process: str = './'):
        super().__init__(dir_process, _Plan)
