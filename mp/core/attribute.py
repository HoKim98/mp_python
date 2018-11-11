from mp.core.error import ConstError, NotDataError, RequiredError, TooMuchOrLessArguments
from mp.core.error import TypeError as _TypeError
from mp.core.expression import Expression as Exp


map_num_type = {
    'b': NotImplemented,
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

        self.is_attr = True
        self.fixed = False

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

    def remove_cache(self):
        if self.toward is not None:
            if not self.toward.fixed:
                self.value = None
                self.toward.remove_cache()

    @property
    def symbol(self):
        if self.name.startswith('/'):
            return self.toward.symbol
        return self.name

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
            raise NotDataError(self.symbol)
        if self.toward is None:
            raise RequiredError(self.symbol)
        return self.to_value(self.toward)

    @classmethod
    def to_value(cls, arg):
        return arg.get_value() if type(arg) in attr_classes else arg

    def __repr__(self):
        return '%s = %s' % (self.name, repr(self.toward))


class AttrConst(Attr):
    def __init__(self, value):
        super().__init__('const')
        self.value = value

    @property
    def symbol(self):
        return self.name

    @property
    def is_constant(self):
        return True

    @property
    def toward(self):
        return self

    def remove_cache(self):
        pass

    @toward.setter
    def toward(self, toward):
        raise ConstError()

    @property
    def reusable(self):
        return True

    def _calculate(self):
        return self.value

    def __repr__(self):
        return self.value


class AttrList:
    ATTR = Attr

    def __init__(self, args, execute_recursive=None):
        if execute_recursive is not None:
            args = [execute_recursive(arg) for arg in args]
        self.list = args

    def get_values(self):
        return [self.ATTR.to_value(arg) for arg in self.list]

    def assert_sizeof(self, symbol: str, expected: int, greater_or_less: int = 0):
        if greater_or_less == 0 and len(self) != expected:
            raise TooMuchOrLessArguments(symbol, expected, len(self), greater_or_less)
        if greater_or_less > 0 and len(self) < expected:
            raise TooMuchOrLessArguments(symbol, expected, len(self), greater_or_less)
        if greater_or_less < 0 and len(self) > expected:
            raise TooMuchOrLessArguments(symbol, expected, len(self), greater_or_less)

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
    def symbol(self):
        return self.name

    @property
    def op(self) -> str:
        return self.name

    @property
    def reusable(self):
        return False

    def remove_cache(self):
        for arg in self.args.list:
            if arg is not None:
                arg.remove_cache()

    def _calculate(self):
        args = self.args.get_values()
        if self.op in self.MAP_OP.keys():
            # check type
            args = args[:2]
            for arg, var_arg in zip(args, self.args.list):
                if hasattr(arg, 'is_data'):
                    if not arg.is_data:
                        raise NotDataError(var_arg.symbol)
                elif arg is None:
                    raise NotDataError(var_arg.symbol)
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

    @property
    def symbol(self):
        return self.sub.symbol

    def _calculate(self):
        sub = self.sub.get_value()
        args = self.args.get_values()

        # dim
        if len(args) == 0:
            return self._calculate_dim(sub)
        # sizeof
        if len(args) == 1:
            return self._calculate_sizeof(sub, args[0])
        # transpose
        return self._calculate_view(sub, args)

    @classmethod
    def _calculate_dim(cls, sub):
        raise NotImplementedError

    @classmethod
    def _calculate_sizeof(cls, sub, axis):
        raise NotImplementedError

    def _calculate_view(self, sub, args):
        raise NotImplementedError

    def _calculate_slice(self, args):
        pass


class AttrIndexed(AttrOP):
    def __init__(self, sub: Attr, args):
        super().__init__(Exp.SHELL_RR[0], args)
        self.sub = sub

    @property
    def symbol(self):
        return self.sub.symbol

    def _calculate(self):
        sub = self.sub.get_value()
        # if method delegate
        if hasattr(sub, 'is_data'):
            if sub.is_method and sub.args is None:
                return self._calculate_method_delegate(sub)

        args = self.args.get_values()
        # copy object
        if len(args) == 0:
            return self._calculate_copy(sub)
        # slicing
        # check size
        dim_sub = self._calculate_dim(sub)
        dim_args = len(args)
        if dim_sub < dim_args:
            raise TooMuchOrLessArguments(self.symbol, dim_sub, dim_args, -1)
        return self._calculate_indexed(sub, args)

    def _calculate_method_delegate(self, sub):
        sub.args = self.args
        return sub.get_value()

    def _calculate_dim(self, sub):
        raise NotImplementedError

    def _calculate_copy(self, sub):
        raise NotImplementedError

    def _calculate_indexed(self, sub, args):
        raise NotImplementedError

    def _calculate_slice(self, args):
        pass


class AttrMethod(Attr):
    def __init__(self, name: str, method, toward, args, fixed, repeat=None):
        super().__init__(name, toward)
        self.is_method = True
        self.method = method
        self.args = args
        self.fixed = fixed

        self.code = toward.encode()
        self.repeat = repeat

    @property
    def symbol(self):
        return self.name

    @property
    def reusable(self):
        return False

    def remove_cache(self):
        if self.args is not None and not self.fixed:
            for arg in self.args.list:
                if arg is not None:
                    arg.remove_cache()

    def _calculate(self):
        # if pointing method
        if self.args is None:
            self.is_data = False
            return self
            # return None
        # if repeat call
        result = self._assert_result_not_none(None)
        if self.repeat is not None:
            num_repeat = int(self.repeat.get_value())
            for _ in range(num_repeat):
                result = self.method.execute(self.toward, self.args)
                result = self._assert_result_not_none(result)
        # else
        else:
            result = self.method.execute(self.toward, self.args)
            result = self._assert_result_not_none(result)
        self.is_data = self.toward.is_data
        return result

    def _assert_result_not_none(self, result):
        if result is None:
            result = 0
        return result


class AttrIteration(AttrMethod):
    CONST = AttrConst

    def __init__(self, name: str, method, toward, placeholders, args, repeat=None):
        super().__init__(name, method, toward, args, False, repeat)
        self.placeholders = placeholders
        self.args_bak = None

    def remove_cache(self):
        for arg in self.args.list:
            if arg is not None:
                arg.remove_cache()

    def _apply_placeholder(self):
        self.args_bak = list()
        for arg_from, arg_to in zip(self.placeholders.list, self.args.list):
            self.args_bak.append(arg_from.toward)
            arg_from.toward = arg_to

    def _revert_placeholder(self):
        for arg_from, arg_to in zip(self.placeholders.list, self.args_bak):
            arg_from.toward = arg_to

    def _calculate(self):
        # fill placeholders into args
        self._apply_placeholder()
        # if normal call
        if self.repeat is None:
            self.fixed = self.method.fixed
            value = self.method.get_value()
            self._revert_placeholder()
            return value
        # if repeat call
        value = None
        # save origin value
        feedback = self.placeholders.list[-1]
        # begin iteration
        for _ in range(int(self.repeat.get_value())):
            # calculate
            value = self.method.get_value()
            # update final value
            final = self.CONST(value)
            feedback.toward = final
        # revert origin value
        self._revert_placeholder()
        return value


class AttrDict:

    def __init__(self):
        self.dict = dict()

    def __getitem__(self, name) -> Attr:
        # create new attr if not exists
        if name not in self.dict.keys():
            self.dict[name] = self._new_attr(name)
        return self.dict[name]

    def _new_attr(self, key):
        return Attr(key)


attr_classes = (Attr, AttrConst, AttrIndexed, AttrIteration, AttrMethod, AttrOP, AttrView)
