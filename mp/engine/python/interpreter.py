from mp.core import Interpreter as _Interpreter
from mp.engine.python.plan import Plan as _Plan


class Interpreter(_Interpreter):
    def __init__(self, dir_process: str = './', *args, **kwargs):
        super().__init__(dir_process, _Plan)
