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
        return torch.full((), fill_value=toward.value, device=Device.get(),
                          dtype=self.ATTR.map_num_type[toward.num_type])
