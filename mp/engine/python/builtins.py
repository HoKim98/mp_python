from mp.core import error
from mp.engine.python.attribute import np as _np

_float_to_int = lambda args: [int(arg) for arg in args]


def __array(toward, args):
    args = _float_to_int(args.get_values())
    value = _np.zeros(shape=args)
    return value


def __max(toward, args):
    args.assert_sizeof(toward.symbol, 2, +1)
    args = args.get_values()
    return max(args)


def __min(toward, args):
    args.assert_sizeof(toward.symbol, 2, +1)
    args = args.get_values()
    return min(args)
