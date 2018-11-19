from mp.core.expression import Expression as Exp
from mp.core.plan import Plan as _Plan

from mp.engine.pytorch import attribute as _attribute
from mp.engine.pytorch import builtins as _builtins
from mp.engine.pytorch.attribute import torch
from mp.engine.pytorch.device import Device
from mp.engine.pytorch.io import IO


class Plan(_Plan):
    ATTR = _attribute
    BUILTINS = _builtins
    CLASS_IO = IO

    def _new_const(self, toward):
        if toward.num_type == Exp.BOOL:
            return bool(toward.value)
        return torch.full((), fill_value=toward.value, device=Device.get(),
                          dtype=self.ATTR.map_num_type[toward.num_type])

    @classmethod
    def _is_item(cls, shape):
        if len(shape) == 0:
            return True
        return len(shape) == 1 and int(shape[0]) == 1

    @classmethod
    def print_var(cls, var, value):
        if type(value) is _attribute.torch.Tensor:
            shape = value.shape
            if cls._is_item(shape):
                value = value.item()
            else:
                shape = [str(s) for s in shape]
                value = ' x '.join(shape)
                value = 'shape(%s)' % value
        super().print_var(var, value)
