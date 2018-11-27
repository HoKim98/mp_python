from mp.core.expression import Expression as Exp
from mp.core.plan import Plan as _Plan

from mp.engine.pytorch import builtins as _builtins
from mp.engine.pytorch import framework
from mp.engine.pytorch.device import Device
from mp.engine.pytorch.io import IO


class Plan(_Plan):
    BUILTINS = _builtins
    CLASS_IO = IO

    MAP_NUM_TYPE = framework.MAP_NUM_TYPE

    def _new_const(self, toward):
        if toward.num_type == Exp.BOOL:
            return bool(toward.value)
        return framework.new_const(toward, Device.get())

    @classmethod
    def _is_item(cls, shape):
        if len(shape) == 0:
            return True
        return len(shape) == 1 and int(shape[0]) == 1

    @classmethod
    def print_var(cls, var, value):
        if type(value) is framework.torch.Tensor:
            shape = value.shape
            if cls._is_item(shape):
                value = value.item()
            else:
                shape = [str(s) for s in shape]
                value = ' x '.join(shape)
                value = 'shape(%s)' % value
        super().print_var(var, value)
