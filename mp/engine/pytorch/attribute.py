import torch

from mp.core import attribute as _attribute
from mp.core.expression import Expression as Exp


map_num_type = {
    # bool-type is not supported
    'b': torch.float64,
    'i8': torch.int8,
    'i16': torch.int16,
    'i32': torch.int32,
    'i64': torch.int64,
    'f16': torch.float16,
    'f32': torch.float32,
    'f64': torch.float64,
}
map_num_type_reversed = {v: k for k, v in map_num_type.items()}
map_op = {
    tuple(Exp.ADD + Exp.IADD): lambda x, y: x + y,
    tuple(Exp.SUB + Exp.ISUB): lambda x, y: x - y,
    tuple(Exp.MUL + Exp.IMUL): lambda x, y: x * y,
    tuple(Exp.TDIV + Exp.ITDIV): lambda x, y: x / y,
    tuple(Exp.MAT + Exp.IMAT): lambda x, y: x @ y,
    tuple(Exp.POW + Exp.IPOW): lambda x, y: x ** y,
    tuple(Exp.FDIV + Exp.IFDIV): lambda x, y: x // y,
    tuple(Exp.MOD + Exp.IMOD): lambda x, y: x % y,

    tuple(Exp.EQ): lambda x, y: x == y,
    tuple(Exp.NEQ): lambda x, y: x != y,
    tuple(Exp.GT): lambda x, y: x > y,
    tuple(Exp.GE): lambda x, y: x >= y,
    tuple(Exp.LT): lambda x, y: x < y,
    tuple(Exp.LE): lambda x, y: x <= y,
}
map_op = {op: order for ops, order in map_op.items() for op in ops}


class Attr(_attribute.Attr):
    @classmethod
    def to_value(cls, arg):
        return arg.get_value() if type(arg) in attr_classes else arg


class AttrConst(_attribute.AttrConst):
    pass


class AttrList(_attribute.AttrList):
    ATTR = Attr


class AttrOP(_attribute.AttrOP):
    MAP_OP = map_op

    def _calculate_slice(self, args):
        return slice(*args)


class AttrView(_attribute.AttrView):
    @classmethod
    def _calculate_dim(cls, sub):
        return sub.dim()

    @classmethod
    def _calculate_sizeof(cls, sub, axis):
        return sub.shape[axis]

    def _calculate_view(self, sub, args):
        return sub.transpose(*args)


class AttrIndexed(_attribute.AttrIndexed):
    def _calculate_dim(self, sub):
        return AttrView._calculate_dim(sub)

    def _calculate_copy(self, sub):
        return sub.clone()

    def _calculate_indexed(self, sub, args):
        args = self._assert_int(args)
        return sub[tuple(args)]

    def _assert_int(self, args):
        args = list(args)
        for i, arg in enumerate(args):
            if arg is None:
                continue
            if type(arg) is slice:
                arg = (self._assert_int_unit(arg.start),
                       self._assert_int_unit(arg.stop),
                       self._assert_int_unit(arg.step))
                args[i] = slice(*arg)
                continue
            args[i] = self._assert_int_unit(arg)
        return args

    def _assert_int_unit(self, arg):
        if arg is None:
            return arg
        return arg.type(torch.int64)


class AttrMethod(_attribute.AttrMethod):
    pass


class AttrDict(_attribute.AttrDict):
    def _new_attr(self, key):
        return Attr(key)


class AttrIteration(_attribute.AttrIteration):
    CONST = AttrConst


attr_classes = (Attr, AttrConst, AttrIndexed, AttrIteration, AttrMethod, AttrOP, AttrView)
