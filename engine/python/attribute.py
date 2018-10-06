from core.expression import Expression as Exp
import numpy as np

from core import attribute as _attribute


map_num_type = {
    'i8': np.int8,
    'i16': np.int16,
    'i32': np.int32,
    'i64': np.int64,
    'f16': np.float16,
    'f32': np.float32,
    'f64': np.float64,
}
map_num_type_reversed = {v: k for k, v in map_num_type.items()}
map_op = {
    tuple(Exp.ADD + Exp.IADD): np.add,
    tuple(Exp.SUB + Exp.ISUB): np.subtract,
    tuple(Exp.MUL + Exp.IMUL): np.multiply,
    tuple(Exp.TDIV + Exp.ITDIV): np.true_divide,
    tuple(Exp.MAT + Exp.IMAT): np.matmul,
    tuple(Exp.POW + Exp.IPOW): np.power,
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


class AttrList(_attribute.AttrList):
    ATTR = Attr


class AttrOP(_attribute.AttrOP):
    MAP_OP = map_op

    def _calculate_slice(self, args):
        return slice(*args)


class AttrView(_attribute.AttrView):
    def _calculate_view(self, sub, args):
        # dim
        if len(args) == 0:
            return np.ndim(sub)
        # sizeof
        if len(args) == 1:
            return np.size(sub, args[0])
        # transpose
        return np.transpose(sub, args)


class AttrIndexed(_attribute.AttrIndexed):
    def _calculate_indexed(self, sub, args):
        # copy object
        if len(args) == 0:
            return np.copy(sub)
        # slicing
        return sub[tuple(args)]


class AttrDict(_attribute.AttrDict):
    def _new_attr(self, key):
        return Attr(key)


attr_classes = (Attr, AttrConst, AttrIndexed, AttrOP, AttrView)
