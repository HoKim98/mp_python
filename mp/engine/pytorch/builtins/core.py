from mp.core import extension as _ext
from mp.engine.pytorch.device import Device
from mp.engine.pytorch.framework import torch as _torch


def _float_to_int(args):
    return [int(arg) for arg in args]


@_ext.static('tensor', fixed=True)
def method_tensor(plan, toward, args, kwargs):
    args = _float_to_int(args.get_value())
    value = _torch.zeros(*args, device=Device.get())
    return value


@_ext.static('rand', fixed=True)
def method_rand(plan, toward, args, kwargs):
    args = _float_to_int(args.get_value())
    value = _torch.rand(*args, device=Device.get())
    return value


@_ext.static('randn', fixed=True)
def method_randn(plan, toward, args, kwargs):
    args = _float_to_int(args.get_value())
    value = _torch.randn(*args, device=Device.get())
    return value


@_ext.static('var', fixed=True)
def method_var(plan, toward, args, kwargs):
    args.assert_sizeof(toward.symbol, 2)
    weight, optim = args.get_value()
    weight.requires_grad_(True)
    optim.add_param_group({'params': weight})
    return weight


@_ext.static('copy')
def method_copy(plan, toward, args, kwargs):
    symbol = '[copy]' if toward is None else toward.symbol
    args.assert_sizeof(symbol, 1)
    sub, = args.get_value()
    return sub.clone()


@_ext.static('float')
def method_float(plan, toward, args, kwargs):
    args.assert_sizeof(toward.symbol, 1)
    x, = args.get_value()
    x = x.float()
    return x


@_ext.static('long')
def method_long(plan, toward, args, kwargs):
    args.assert_sizeof(toward.symbol, 1)
    x, = args.get_value()
    x = x.long()
    return x
