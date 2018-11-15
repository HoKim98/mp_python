from mp.core import extension as _ext
from mp.engine.pytorch.attribute import torch as _torch


@_ext.static('__abs', fixed=True)
def method_math_abs(toward, args, plan):
    args.assert_sizeof(toward.symbol, 1)
    x, = args.get_value()
    x = x.abs()
    return x
