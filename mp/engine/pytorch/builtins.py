from mp.core import extension
from mp.engine.pytorch.attribute import torch as _torch

_float_to_int = lambda args: [int(arg) for arg in args]


@extension.static('array')
def method_array(toward, args):
    args = _float_to_int(args.get_values())
    value = _torch.zeros(*args)
    return value


@extension.static('max')
def method_max(toward, args):
    args.assert_sizeof(toward.symbol, 2, +1)
    args = args.get_values()
    return max(args)


@extension.static('min')
def method_min(toward, args):
    args.assert_sizeof(toward.symbol, 2, +1)
    args = args.get_values()
    return min(args)
