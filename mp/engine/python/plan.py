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

    @classmethod
    def _is_item(cls, shape):
        if len(shape) == 0:
            return True
        return len(shape) == 1 and int(shape[0]) == 1

    @classmethod
    def print_var(cls, var, value):
        if type(value) is _attribute.np.ndarray:
            shape = value.shape
            if cls._is_item(shape):
                value = value.item()
            else:
                shape = [str(s) for s in shape]
                value = ' x '.join(shape)
                value = 'shape(%s)' % value
        super().print_var(var, value)
