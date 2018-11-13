from mp.core import extension
from mp.engine.python.attribute import np as _np

_float_to_int = lambda args: [int(arg) for arg in args]


@extension.static('tensor', fixed=True)
def method_tensor(toward, args, plan):
    args = _float_to_int(args.get_value())
    value = _np.zeros(shape=args)
    return value


@extension.static('max')
def method_max(toward, args, plan):
    args.assert_sizeof(toward.symbol, 2, +1)
    args = args.get_value()
    return max(args)


@extension.static('min')
def method_min(toward, args, plan):
    args.assert_sizeof(toward.symbol, 2, +1)
    args = args.get_value()
    return min(args)
