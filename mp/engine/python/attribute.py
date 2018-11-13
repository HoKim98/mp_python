import numpy as np

from mp.core import attribute as _attribute
from mp.core.expression import Expression as Exp


map_num_type = {
    'b': np.bool,
    'i8': np.uint8,
    'i32': np.int32,
    'i64': np.int64,
    'f16': np.float16,
    'f32': np.float32,
    'f64': np.float64,
}
map_op = {
    tuple(Exp.ADD + Exp.IADD): np.add,
    tuple(Exp.SUB + Exp.ISUB): np.subtract,
    tuple(Exp.MUL + Exp.IMUL): np.multiply,
    tuple(Exp.TDIV + Exp.ITDIV): np.true_divide,
    tuple(Exp.MAT + Exp.IMAT): np.matmul,
    tuple(Exp.POW + Exp.IPOW): np.power,
    tuple(Exp.FDIV + Exp.IFDIV): np.floor_divide,
    tuple(Exp.MOD + Exp.IMOD): np.fmod,

    tuple(Exp.EQ): np.equal,
    tuple(Exp.NEQ): np.not_equal,
    tuple(Exp.GT): np.greater,
    tuple(Exp.GE): np.greater_equal,
    tuple(Exp.LT): np.less,
    tuple(Exp.LE): np.less_equal,
}
map_op = {op: order for ops, order in map_op.items() for op in ops}


class Attr(_attribute.Attr):
    @classmethod
    def to_value(cls, arg):
        return arg.get_value() if type(arg) in attr_classes else arg


class AttrConst(_attribute.AttrConst):
    pass


class AttrTuple(_attribute.AttrTuple):
    ATTR = Attr


class AttrOP(_attribute.AttrOP):
    MAP_OP = map_op

    def _calculate_slice(self, args):
        return slice(*args)


class AttrView(_attribute.AttrView):
    @classmethod
    def _calculate_dim(cls, sub):
        return np.ndim(sub)

    @classmethod
    def _calculate_sizeof(cls, sub, axis):
        return np.size(sub, axis)

    def _calculate_view(self, sub, args):
        dim = np.ndim(sub)
        if len(args) < dim:
            args += list(range(len(args), dim))
        return np.transpose(sub, args)


class AttrIndexed(_attribute.AttrIndexed):
    def _calculate_dim(self, sub):
        return AttrView._calculate_dim(sub)

    def _calculate_copy(self, sub):
        return np.copy(sub)

    def _calculate_indexed(self, sub, args):
        return sub[tuple(args)]


class AttrMethod(_attribute.AttrMethod):
    pass


class AttrDict(_attribute.AttrDict):
    def _new_attr(self, key):
        return Attr(key)


class AttrIteration(_attribute.AttrIteration):
    CONST = AttrConst


attr_classes = (Attr, AttrConst, AttrIndexed, AttrIteration, AttrMethod, AttrOP, AttrTuple, AttrView)
