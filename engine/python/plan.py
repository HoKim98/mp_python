from core.plan import Plan as _Plan

from engine.python import attribute as _attribute
from engine.python import builtins as _builtins
from engine.python.attribute import np
from engine.python.io import IO


class Plan(_Plan):
    ATTR = _attribute
    BUILTINS = _builtins
    CLASS_IO = IO

    def _new_const(self, toward):
        return np.full(shape=(), fill_value=toward.value,
                       dtype=self.ATTR.map_num_type[toward.num_type])
