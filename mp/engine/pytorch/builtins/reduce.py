from mp.core import extension as _ext
from mp.engine.pytorch.framework import torch as _torch


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


@_ext.static('__reduce_slice')
def method_reduce_slice(toward, args, plan):
    symbol = '[slice]' if toward is None else toward.symbol
    args.assert_sizeof(symbol, 3)
    args = args.get_value()
    return slice(*args)


@_ext.static('__reduce_dim')
def method_reduce_dim(toward, args, plan):
    symbol = '[dim]' if toward is None else toward.symbol
    args.assert_sizeof(symbol, 1)
    sub, = args.get_value()
    return sub.dim()


@_ext.static('__reduce_sizeof')
def method_reduce_sizeof(toward, args, plan):
    symbol = '[sizeof]' if toward is None else toward.symbol
    args.assert_sizeof(symbol, 2)
    sub, axis = args.get_value()
    return sub.shape[axis]


@_ext.static('__reduce_transpose')
def method_reduce_transpose(toward, args, plan):
    symbol = '[transpose]' if toward is None else toward.symbol
    args.assert_sizeof(symbol, 3)
    sub, *args = args.get_value()
    return sub.transpose(*args)


@_ext.static('__reduce_indexed')
def method_reduce_indexed(toward, args, plan):
    symbol = '[indexed]' if toward is None else toward.symbol
    args.assert_sizeof(symbol, 2, +1)
    sub, *args = args.get_value()

    def _assert_int_unit(_arg):
        if _arg is None:
            return _arg
        return int(_arg)

    for i, arg in enumerate(args):
        if arg is None:
            continue
        if type(arg) is slice:
            arg = (_assert_int_unit(arg.start),
                   _assert_int_unit(arg.stop),
                   _assert_int_unit(arg.step))
            args[i] = slice(*arg)
            continue
        args[i] = _assert_int_unit(arg)
    return sub[tuple(args)]


@_ext.static('__reduce_view')
def method_reduce_view(toward, args, plan):
    symbol = '[view]' if toward is None else toward.symbol
    args.assert_sizeof(symbol, 1, +1)
    sub, *args = args.get_value()
    return sub.view(*args)
