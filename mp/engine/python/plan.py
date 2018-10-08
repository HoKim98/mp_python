from mp.core.plan import Plan as _Plan

from mp.engine.python import attribute as _attribute
from mp.engine.python import builtins as _builtins
from mp.engine.python.attribute import np
from mp.engine.python.io import IO


class Plan(_Plan):
    ATTR = _attribute
    BUILTINS = _builtins
    CLASS_IO = IO

    def _new_const(self, toward):
        return np.full(shape=(), fill_value=toward.value,
                       dtype=self.ATTR.map_num_type[toward.num_type])
