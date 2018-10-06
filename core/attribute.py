from core.error import ConstError, RequiredError
from core.expression import Expression as Exp


map_num_type = {
    'i8': NotImplemented,
    'i16': NotImplemented,
    'i32': NotImplemented,
    'i64': NotImplemented,
    'f16': NotImplemented,
    'f32': NotImplemented,
    'f64': NotImplemented,
}
map_num_type_reversed = {v: k for k, v in map_num_type.items()}
map_op = {
    tuple(Exp.ADD + Exp.IADD): NotImplemented,
    tuple(Exp.SUB + Exp.ISUB): NotImplemented,
    tuple(Exp.MUL + Exp.IMUL): NotImplemented,
    tuple(Exp.TDIV + Exp.ITDIV): NotImplemented,
    tuple(Exp.MAT + Exp.IMAT): NotImplemented,
    tuple(Exp.POW + Exp.IPOW): NotImplemented,
    tuple(Exp.POW + Exp.IPOW): NotImplemented,
    tuple(Exp.FDIV + Exp.IFDIV): NotImplemented,
    tuple(Exp.MOD + Exp.IMOD): NotImplemented,

    tuple(Exp.EQ): NotImplemented,
    tuple(Exp.NEQ): NotImplemented,
    tuple(Exp.GT): NotImplemented,
    tuple(Exp.GE): NotImplemented,
    tuple(Exp.LT): NotImplemented,
    tuple(Exp.LE): NotImplemented,
}
map_op = {op: order for ops, order in map_op.items() for op in ops}


class Attr:
    def __init__(self, name: str, toward=None):
        self.name = name
        self._toward = toward
        self.code = None
        self.value = None

    def get_value(self):
        if not self.reusable:
            self.value = self._calculate()
        return self.value

    @property
    def is_constant(self):
        return False

    @property
    def toward(self):
        return self._toward

    @toward.setter
    def toward(self, toward):
        self.value = None
        self._toward = toward

    @property
    def reusable(self):
        return self.value is not None

    def _calculate(self):
        if self.toward is None:
            raise RequiredError(self.name)
        return self.to_value(self.toward)

    @classmethod
    def to_value(cls, arg):
        return arg.get_value() if type(arg) in attr_classes else arg

    def __repr__(self):
        return '%s = %s' % (self.name, repr(self.toward))


class AttrConst(Attr):
    def __init__(self, code, value):
        super().__init__('const')
        self.code = code
        self.value = value

    @property
    def is_constant(self):
        return True

    @property
    def toward(self):
        return self

    @toward.setter
    def toward(self, toward):
        raise ConstError()

    @property
    def reusable(self):
        return True

    def _calculate(self):
        return self.value

    def __repr__(self):
        return self.name


class AttrList:
    ATTR = Attr

    def __init__(self, args, execute_recursive=None):
        if execute_recursive is not None:
            args = [execute_recursive(arg) for arg in args]
        self.list = args

    def get_values(self):
        return [self.ATTR.to_value(arg) for arg in self.list]

    def __repr__(self):
        return repr(self.list)


class AttrOP(Attr):
    MAP_OP = map_op

    def __init__(self, op: str, args):
        super().__init__(op)
        self.args = args

    @property
    def op(self) -> str:
        return self.name

    @property
    def reusable(self):
        return False

    def _calculate(self):
        args = self.args.get_values()
        if self.op in self.MAP_OP.keys():
            return self.MAP_OP[self.op](*args[:2])
        if self.op in Exp.IDX:
            return self._calculate_slice(args)
        raise NotImplementedError

    def _calculate_slice(self, args):
        raise NotImplementedError


class AttrView(AttrOP):
    def __init__(self, sub, args):
        super().__init__('{}', args)  # TODO
        self.sub = sub

    def _calculate(self):
        sub = self.sub.get_value()
        args = self.args.get_values()
        return self._calculate_view(sub, args)

    def _calculate_view(self, sub, args):
        raise NotImplementedError

    def _calculate_slice(self, args):
        pass


class AttrIndexed(AttrOP):
    def __init__(self, sub: Attr, args):
        super().__init__('()', args)  # TODO
        self.sub = sub

    def _calculate(self):
        sub = self.sub.get_value()
        args = self.args.get_values()
        return self._calculate_indexed(sub, args)

    def _calculate_indexed(self, sub, args):
        raise NotImplementedError

    def _calculate_slice(self, args):
        pass


class AttrDict:

    def __init__(self):
        self.dict = dict()

    def __getitem__(self, name) -> Attr:
        if name not in self.dict.keys():
            self.dict[name] = self._new_attr(name)
        return self.dict[name]

    def _new_attr(self, key):
        return Attr(key)


attr_classes = (Attr, AttrConst, AttrIndexed, AttrOP, AttrView)
