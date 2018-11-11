from mp.core import extension as _ext
from mp.engine.pytorch.attribute import torch as _torch
from mp.engine.pytorch.device import Device


def _float_to_int(args):
    return [int(arg) for arg in args]


@_ext.static('array', fixed=True)
def method_array(toward, args):
    args = _float_to_int(args.get_values())
    value = _torch.zeros(*args, device=Device.get())
    return value


@_ext.static('rand', fixed=True)
def method_rand(toward, args):
    args = _float_to_int(args.get_values())
    value = _torch.rand(*args, device=Device.get())
    return value


@_ext.static('randn', fixed=True)
def method_randn(toward, args):
    args = _float_to_int(args.get_values())
    value = _torch.randn(*args, device=Device.get())
    return value


@_ext.static('var', fixed=True)
def method_var(toward, args):
    args.assert_sizeof(toward.symbol, 2)
    weight, optim = args.get_values()
    weight.requires_grad_(True)
    optim.add_param_group({'params': weight})
    return weight
