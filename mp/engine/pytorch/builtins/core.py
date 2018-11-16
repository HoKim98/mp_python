from mp.core import extension as _ext
from mp.engine.pytorch.attribute import torch as _torch
from mp.engine.pytorch.device import Device


def _float_to_int(args):
    return [int(arg) for arg in args]


@_ext.static('tensor', fixed=True)
def method_tensor(toward, args, plan):
    args = _float_to_int(args.get_value())
    value = _torch.zeros(*args, device=Device.get())
    return value


@_ext.static('rand', fixed=True)
def method_rand(toward, args, plan):
    args = _float_to_int(args.get_value())
    value = _torch.rand(*args, device=Device.get())
    return value


@_ext.static('randn', fixed=True)
def method_randn(toward, args, plan):
    args = _float_to_int(args.get_value())
    value = _torch.randn(*args, device=Device.get())
    return value


@_ext.static('var', fixed=True)
def method_var(toward, args, plan):
    args.assert_sizeof(toward.symbol, 2)
    weight, optim = args.get_value()
    weight.requires_grad_(True)
    optim.add_param_group({'params': weight})
    return weight


@_ext.static('float')
def method_float(toward, args, plan):
    args.assert_sizeof(toward.symbol, 1)
    x, = args.get_value()
    x = x.float()
    return x


@_ext.static('long')
def method_long(toward, args, plan):
    args.assert_sizeof(toward.symbol, 1)
    x, = args.get_value()
    x = x.long()
    return x
