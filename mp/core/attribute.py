from mp.core.error import ConstError, NotDataError, RequiredError
from mp.core.error import TypeError as _TypeError
from mp.core.expression import Expression as Exp


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

        # callable or constant
        self.is_data = True
        self.is_method = False

        # repeat call
        self.repeat = None

    def get_value(self):
        if not self.reusable:
            self.value = self._calculate()
            if self.toward is not None:
                self.is_data = self.toward.is_data
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
        if not self.is_data:
            raise NotDataError(self.name)
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

    def __getitem__(self, item):
        raise NotImplementedError

    def __repr__(self):
        return repr(self.list)

    def __len__(self):
        return len(self.list)


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
            # check type
            args = args[:2]
            for arg in args:
                if hasattr(arg, 'is_data'):
                    if not arg.is_data:
                        raise NotDataError(arg.sub)
            # check type (unexpected)
            try:
                return self.MAP_OP[self.op](*args)
            except TypeError as e:
                raise _TypeError(str(e))
        if self.op in Exp.IDX:
            return self._calculate_slice(args)
        raise NotImplementedError

    def _calculate_slice(self, args):
        raise NotImplementedError


class AttrView(AttrOP):
    def __init__(self, sub, args):
        super().__init__(Exp.SHELL_AA[0], args)
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
        super().__init__(Exp.SHELL_RR[0], args)
        self.sub = sub

    def _calculate(self):
        sub = self.sub.get_value()
        args = self.args.get_values()
        return self._calculate_indexed(sub, args)

    def _calculate_indexed(self, sub, args):
        raise NotImplementedError

    def _calculate_slice(self, args):
        pass


class AttrMethod(Attr):
    def __init__(self, name: str, method, toward, args, repeat=None):
        super().__init__(name, toward)
        self.is_method = True
        self.method = method
        self.args = args

        self.code = toward.encode()
        self.repeat = repeat

    @property
    def reusable(self):
        return False

    def _calculate(self):
        # if pointing method
        if self.args is None:
            self.is_data = False
            return None
        # if repeat call
        result = None
        if self.repeat is not None:
            num_repeat = int(self.repeat.get_value())
            for _ in range(num_repeat):
                result = self.method(self.toward, self.args)
        # else
        else:
            result = self.method(self.toward, self.args)
        self.is_data = self.toward.is_data
        return result


class AttrDict:

    def __init__(self):
        self.dict = dict()

    def __getitem__(self, name) -> Attr:
        if name not in self.dict.keys():
            self.dict[name] = self._new_attr(name)
        return self.dict[name]

    def _new_attr(self, key):
        return Attr(key)


attr_classes = (Attr, AttrConst, AttrIndexed, AttrMethod, AttrOP, AttrView)
