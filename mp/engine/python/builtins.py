from mp.core import error
from mp.engine.python import attribute as attr
from mp.engine.python.attribute import np as _np

_max = max
_min = min

_const = lambda toward, value: attr.AttrConst(toward, value)
_float_to_int = lambda args: [int(arg) for arg in args]


def array(toward, args):
    args = _float_to_int(args.get_values())
    value = _np.zeros(shape=args)
    return _const(toward, value)


def max(toward, args):
    args = args.get_values()
    if len(args) < 2:
        raise error.TooMuchOrLessArguments(toward.sub, 2, len(args), +1)
    return _const(toward, _max(args))


def min(toward, args):
    args = args.get_values()
    if len(args) < 2:
        raise error.TooMuchOrLessArguments(toward.sub, 2, len(args), +1)
    return _const(toward, _min(args))
