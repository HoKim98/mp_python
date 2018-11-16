from mp.core import extension as _ext
from mp.engine.pytorch.attribute import torch as _torch


@_ext.static('max')
def method_reduce_max(toward, args, plan):
    args.assert_sizeof(toward.symbol, 2, +1)
    args = args.get_value()
    return _torch.max(*args)


@_ext.static('min')
def method_reduce_min(toward, args, plan):
    args.assert_sizeof(toward.symbol, 2, +1)
    args = args.get_value()
    return _torch.min(*args)


@_ext.static('sum')
def method_reduce_sum(toward, args, plan):
    args.assert_sizeof(toward.symbol, 1, +1)
    x, *dim = args.get_value()
    return _torch.sum(x, *dim)


@_ext.static('mean')
def method_reduce_mean(toward, args, plan):
    args.assert_sizeof(toward.symbol, 1, +1)
    x, *dim = args.get_value()
    return _torch.mean(x, *dim)
