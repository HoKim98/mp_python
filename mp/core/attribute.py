from mp.core.error import ConstError, NotDataError, RequiredError, TooMuchOrLessArguments
from mp.core.error import TypeError as _TypeError
from mp.core.event import Event
from mp.core.expression import Expression as Exp


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


class AttrTuple(Attr):
    ATTR = Attr

    def __init__(self, args, execute_recursive=None):
        super().__init__(Exp.TUPLE)
        if execute_recursive is not None:
            args = [execute_recursive(arg) for arg in args]
        self.list = args
        self._execute_recursive = execute_recursive

    def get_value(self):
        return [self.ATTR.to_value(arg) for arg in self.list]

    def remove_cache(self):
        for arg in self.list:
            if arg is not None:
                arg.remove_cache()

    def assert_sizeof(self, symbol: str, expected: int, greater_or_less: int = 0):
        if greater_or_less == 0 and len(self) != expected:
            raise TooMuchOrLessArguments(symbol, expected, len(self), greater_or_less)
        if greater_or_less > 0 and len(self) < expected:
            raise TooMuchOrLessArguments(symbol, expected, len(self), greater_or_less)
        if greater_or_less < 0 and len(self) > expected:
            raise TooMuchOrLessArguments(symbol, expected, len(self), greater_or_less)

    @classmethod
    def assert_false_to_none(cls, value):
        if value is not None:
            if type(value) is bool:
                return None if not value else True
        return value

    def copy(self, *pre_args):
        return self.__class__(list(pre_args) + self.list.copy())

    def __repr__(self):
        args = []
        for arg in self.list:
            if hasattr(arg, 'is_data'):
                args.append(str(arg.get_value()))
            else:
                args.append(str(arg))
        return '%s%s%s' % (Exp.RBO[0], ', '.join(args), Exp.RBC[0])

    def __len__(self):
        return len(self.list)


class AttrOP(Attr):
    MAP_OP = {
        tuple(Exp.ADD + Exp.IADD): Event.delegate('__math_add'),
        tuple(Exp.SUB + Exp.ISUB): Event.delegate('__math_sub'),
        tuple(Exp.MUL + Exp.IMUL): Event.delegate('__math_mul'),
        tuple(Exp.TDIV + Exp.ITDIV): Event.delegate('__math_tdiv'),
        tuple(Exp.MAT + Exp.IMAT): Event.delegate('__math_mat'),
        tuple(Exp.POW + Exp.IPOW): Event.delegate('__math_pow'),
        tuple(Exp.FDIV + Exp.IFDIV): Event.delegate('__math_fdiv'),
        tuple(Exp.MOD + Exp.IMOD): Event.delegate('__math_mod'),

        tuple(Exp.EQ): Event.delegate('__math_eq'),
        tuple(Exp.NEQ): Event.delegate('__math_neq'),
        tuple(Exp.GT): Event.delegate('__math_gt'),
        tuple(Exp.GE): Event.delegate('__math_ge'),
        tuple(Exp.LT): Event.delegate('__math_lt'),
        tuple(Exp.LE): Event.delegate('__math_le'),
    }
    MAP_OP = {op: order for ops, order in MAP_OP.items() for op in ops}

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
        if self.op in self.MAP_OP.keys():
            args = self.args.get_value()
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
            return self._calculate_slice(self.args)
        raise NotImplementedError

    @classmethod
    def _calculate_slice(cls, args):
        return Exp.EVENT('__reduce_slice', None, None, args, {})


class AttrShell(AttrOP):
    def __init__(self, op: str, sub: Attr, args):
        super().__init__(op, args)
        self.sub = sub

    @property
    def symbol(self):
        return self.sub.symbol

    def remove_cache(self):
        self.sub.remove_cache()
        super().remove_cache()

    def _calculate_indexed(self, sub, args):
        pass

    def _calculate_slice(self, args):
        pass


class AttrTranspose(AttrShell):
    def __init__(self, sub, args):
        super().__init__(Exp.SHELL_AA[0], sub, args)

    def _calculate(self):
        args = self.args.copy()
        # dim
        if len(self.args) == 0:
            del args.list[0:]
            args.list.append(self.sub)
            return self._calculate_dim(args)
        # sizeof
        if len(self.args) == 1:
            del args.list[1:]
            return self._calculate_sizeof(self.sub, args)
        # transpose
        return self._calculate_transpose(self.sub, args)

    @classmethod
    def _calculate_dim(cls, sub):
        return Exp.EVENT('__reduce_dim', None, None, sub, {})

    @classmethod
    def _calculate_sizeof(cls, sub, axis):
        args = axis.copy(sub)
        return Exp.EVENT('__reduce_sizeof', None, None, args, {})

    @classmethod
    def _calculate_transpose(cls, sub, args):
        args = args.copy(sub)
        return Exp.EVENT('__reduce_transpose', None, None, args, {})


class AttrIndexed(AttrShell):
    def __init__(self, sub: Attr, args):
        super().__init__(Exp.SHELL_RR[0], sub, args)

    def _calculate(self):
        # if method delegate
        if hasattr(self.sub, 'is_pointer'):
            if self.sub.is_pointer:
                return self._calculate_method_delegate(self.sub)

        args = self.args.copy()
        # copy object
        if len(args) == 0:
            del args.list[0:]
            args.list.append(self.sub)
            return self._calculate_copy(args)
        # slicing
        # check size
        del args.list[0:]
        args.list.append(self.sub)
        dim_sub = self._calculate_dim(args)
        dim_args = len(args)
        if dim_sub < dim_args:
            raise TooMuchOrLessArguments(self.symbol, dim_sub, dim_args, -1)
        return self._calculate_indexed(self.sub, self.args)

    def _calculate_method_delegate(self, sub):
        sub.args = self.args
        return sub.get_value()

    @classmethod
    def _calculate_dim(cls, sub):
        return AttrTranspose._calculate_dim(sub)

    @classmethod
    def _calculate_copy(cls, sub):
        return Exp.EVENT('copy', None, None, sub, {})

    @classmethod
    def _calculate_indexed(cls, sub, args):
        args = args.copy(sub)
        return Exp.EVENT('__reduce_indexed', None, None, args, {})


class AttrView(AttrShell):
    def __init__(self, sub: Attr, args):
        super().__init__(Exp.SHELL_SS[0], sub, args)

    def _calculate(self):
        return self._calculate_view(self.sub, self.args)

    @classmethod
    def _calculate_view(cls, sub, args):
        args = args.copy(sub)
        return Exp.EVENT('__reduce_view', None, None, args, {})


class AttrMethod(Attr):
    def __init__(self, plan, name: str, method, toward, args, kwargs, fixed, repeat=None):
        super().__init__(name, toward)
        self.is_method = True
        self.method = method
        self.args = args
        self.kwargs = kwargs
        self.fixed = fixed

        self.plan = plan

        self.code = toward.encode()
        self.repeat = repeat

    @property
    def symbol(self):
        return self.name

    @property
    def reusable(self):
        return super().reusable and self.fixed

    @property
    def is_pointer(self):
        return self.args is None

    def remove_cache(self):
        if self.args is not None and not self.fixed:
            for arg in self.args.list:
                if arg is not None:
                    arg.remove_cache()

    def _calculate(self):
        # if pointing method
        if self.is_pointer:
            self.is_data = False
            return self
            # return None
        # if repeat call
        result = self._assert_result_not_none(None)
        if self.repeat is not None:
            num_repeat = int(self.repeat.get_value())
            for _ in range(num_repeat):
                result = self.method(self.plan, self.toward, self.args, self.kwargs)
                result = self._assert_result_not_none(result)
        # else
        else:
            result = self.method(self.plan, self.toward, self.args, self.kwargs)
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
        super().__init__(None, name, method, toward, args, {}, False, repeat)
        self.placeholders = placeholders
        self.args_bak = None

    def remove_cache(self):
        self.method.remove_cache()
        for arg in self.placeholders.list + self.args.list:
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
    ATTR = Attr

    def __init__(self, kwargs=None, execute_recursive=None):
        if execute_recursive is not None:
            kwargs = {key: execute_recursive(value) for key, value in kwargs.items()}
        self.dict = kwargs or {}
        self._execute_recursive = execute_recursive

    def get_value(self):
        return {key: self.ATTR.to_value(value) for key, value in self.dict.items()}

    def __getitem__(self, name) -> Attr:
        # create new attr if not exists
        if name not in self.dict.keys():
            self.dict[name] = self._new_attr(name)
        return self.dict[name]

    def _new_attr(self, key):
        return Attr(key)


attr_classes = (Attr, AttrConst, AttrIndexed, AttrIteration, AttrMethod, AttrOP, AttrTranspose, AttrTuple, AttrView)
