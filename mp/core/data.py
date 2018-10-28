from mp.core.expression import Expression as Exp


class Variable:

    def __init__(self, name: str = None, toward=None):
        self.name = name
        self.toward = toward

        self.num_type = None
        self.value = None
        self.sub = None
        self.obj = None
        self.step = None
        self.args = []

        self.is_pointer = False
        self.is_pointer_orient = False
        self.is_constant = False
        self.is_operator = False
        self.is_indices = False
        self.is_view = False
        self.is_tuple = False
        self.is_method = False
        self.is_method_delegate = False
        self.is_method_defined = False

        self.is_builtins = False
        # callable or constant
        self.is_data = True
        # repeat call
        self.repeat = None

    def has_attr(self, name: str):
        if self.name == name:
            return True
        if self.toward is not None:
            return self.toward.has_attr(name)
        return False

    def copy(self, recursive: bool = False):
        new_var = self.__class__()
        for key, value in self.__dict__.items():
            if recursive and value is not None:
                value = self._copy_recursive(value)
            setattr(new_var, key, value)
        return new_var

    def replace(self, name: str, value=None):
        if self.name == name:
            return self.toward if value is None else value
        self.toward = self._replace(self.toward, name, value)
        return self

    @property
    def is_none(self):
        return (self.name is not None) and (self.toward is None)

    @property
    def is_variable(self):
        return (not self.is_constant) and (not self.is_operator) and (not self.is_method)

    @property
    def is_required(self):
        return self.is_variable and self.toward is None

    @property
    def symbol(self):
        if self.name is not None:
            # is constant
            if self.name.startswith('/'):
                return self.toward.symbol
            return self.name
        raise NotImplementedError

    def encode(self, stack_called=None):
        stack_called = self._ensure_stack_not_none(stack_called)
        toward = self._encode(self.toward, stack_called)
        if self._name_is_constant():
            return toward
        name = self.name
        # if already defined
        if name in stack_called:
            return name
        stack_called.add(name)
        # if required
        if toward is None:
            return name
        # = :=
        op = Exp.DIS[0] if self.is_pointer_orient else Exp.IS[0]
        return '%s%s%s%s%s' % (Exp.RBO[0], name, op, toward, Exp.RBC[0])

    @staticmethod
    def _encode(self, stack_called):
        if self is None:
            return None
        return self.encode(stack_called)

    @staticmethod
    def _ensure_stack_not_none(stack_called):
        if stack_called is None:
            stack_called = set()
        return stack_called

    @classmethod
    def _copy_recursive(cls, value):
        if value is None:
            return None
        # is list
        if type(value) is list:
            return [cls._copy_recursive(a) for a in value]
        # is data
        if hasattr(value, 'copy'):
            return value.copy(recursive=True)
        return value

    @staticmethod
    def _replace(self, name: str, value):
        if self is None:
            return None
        return self.replace(name, value)

    def _name_is_constant(self):
        if self.name is None:
            return True
        return self.name.startswith('/')

    def __bool__(self):
        if self.is_constant:
            return bool(self.value)
        return True

    def __repr__(self):
        return self.encode()


class Constant(Variable):

    def __init__(self, name: str = None, num_type=None, value=None):
        super().__init__(name, self)
        self.is_constant = True
        self.num_type = num_type
        self.value = value

    def has_attr(self, name: str):
        return self.name == name

    def replace(self, name: str, value=None):
        return self

    @property
    def symbol(self):
        return str(self.value)

    def encode(self, stack_called=None):
        value = self.value
        # boolean to numeric
        if self.num_type == Exp.BOOL:
            value = 1 if value else 0
        return '%s%s' % (str(value), self.num_type)

    def __repr__(self):
        return '%s' % str(self.value)


def Required():
    return Variable()


class Operator(Variable):

    def __init__(self, op: str = None, sub: Variable = None, obj: Variable = None, step: Variable = None):
        super().__init__(op)
        self.is_operator = True
        self.sub = sub
        self.obj = obj
        self.step = step

    def has_attr(self, name: str):
        args = [self.sub, self.obj, self.step]
        for arg in args:
            if arg is not None:
                if arg.has_attr(name):
                    return True
        return False

    def replace(self, name: str, value=None):
        self.sub = self._replace(self.sub, name, value)
        self.obj = self._replace(self.obj, name, value)
        self.step = self._replace(self.step, name, value)
        self.args = [self._replace(arg, name, value) for arg in self.args]
        return self

    @property
    def symbol(self):
        return self.name

    @property
    def op(self):
        return self.name

    def encode(self, stack_called=None):
        stack_called = self._ensure_stack_not_none(stack_called)
        # inplace to outplace
        op = self.name
        if op in Exp.Tokens_In2Out.keys():
            op = Exp.Tokens_In2Out[op]
        # :
        elif op in Exp.IDX:
            return self._encode_idx(op, stack_called)
        # else
        return '%s%s%s%s%s' % (Exp.RBO[0],
                               self._encode(self.sub, stack_called), op, self._encode(self.obj, stack_called),
                               Exp.RBC[0])

    def _encode_idx(self, op, stack_called):
        start = self._encode(self.sub, stack_called)
        stop = self._encode(self.obj, stack_called)
        step = self._encode(self.step, stack_called)
        start = '%s%s' % (start, op) if self.sub is not None else '%s' % op
        stop = '%s' % stop if self.obj is not None else ''
        step = '%s%s' % (op, step) if step is not None else ''
        return '%s%s%s' % (start, stop, step)


class Indexed(Operator):

    def __init__(self, sub, *indices):
        super().__init__(Exp.SHELL_RR[0], Required())
        self.is_indices = True
        self.sub = sub
        self.args = indices

    def encode(self, stack_called=None):
        stack_called = self._ensure_stack_not_none(stack_called)
        args = [self._encode(arg, stack_called) for arg in self.args]
        return '%s%s%s%s' % (self._encode(self.sub, stack_called), Exp.RBO[0], Exp.COMMA.join(args), Exp.RBC[0])


class View(Operator):

    def __init__(self, sub, *dims):
        super().__init__(Exp.SHELL_AA[0], Required())
        self.is_view = True
        self.sub = sub
        self.args = dims

    def encode(self, stack_called=None):
        stack_called = self._ensure_stack_not_none(stack_called)
        args = [self._encode(arg, stack_called) for arg in self.args]
        return '%s%s%s%s' % (self._encode(self.sub, stack_called), Exp.ABO[0], Exp.COMMA.join(args), Exp.ABC[0])


class Tuple(Operator):

    def __init__(self, *args):
        super().__init__(Exp.TUPLE, Required())
        self.is_tuple = True
        self.args = args

    def encode(self, stack_called=None):
        stack_called = self._ensure_stack_not_none(stack_called)
        args = [self._encode(arg, stack_called) for arg in self.args]
        return '%s%s%s' % (Exp.RBO[0], Exp.COMMA.join(args), Exp.RBC[0])


class Method(Variable):

    def __init__(self, name=None, toward=None, *args, repeat=None):
        super().__init__(name, toward)
        self.is_method_delegate = True
        self.is_method = True
        self.is_data = False
        self.args = args

        self.repeat = repeat

    def has_attr(self, name: str):
        if self.name == name:
            return True
        if self.toward is not None:
            if self.toward.has_attr(name):
                return True
        for arg in self.args:
            if arg is not None:
                if arg.has_attr(name):
                    return True
        return False

    def replace(self, name: str, value=None):
        sub = super().replace(name, value)
        if not self.is_method_delegate:
            sub.args = [self._replace(arg, name, value) for arg in sub.args]
        return sub

    def get_real_method(self):
        if self.args is None and self.toward is None:
            return self.name
        if self.toward is not None:
            return self.toward.symbol
        raise NotImplementedError

    @property
    def symbol(self):
        return self.name

    def encode(self, stack_called=None):
        stack_called = self._ensure_stack_not_none(stack_called)
        name = self.name
        # not defined yet
        if name not in stack_called:
            stack_called.add(name)
            # has point
            if self.toward is not None:
                toward = self._encode(self.toward, stack_called)
                # name = '%s%s%s' % (name, Exp.IS[0], toward)
                name = '%s' % toward
                # is user-defined method
                if self.toward.is_method_defined and not self.name.startswith(Exp.CODE_CONST):
                    name = '%s%s%s' % (self.name, Exp.IS[0], name)
        # has repeat
        repeat = self._encode_repeat()
        if repeat is not None:
            repeat = self._encode(self.repeat, stack_called)
            name = '%s%s%s' % (name, Exp.MUL[0], repeat)
        # callable
        if not self.is_method_delegate:
            args = [self._encode(arg, stack_called) for arg in self.args]
            # has one argument
            if len(args) == 1:
                args = '%s' % args[0]
            else:
                args = '%s' % Exp.COMMA.join(args)
            # not just mention (sub)
            if name != self.name:
                name = '%s%s%s' % (Exp.RBO[0], name, Exp.RBC[0])
            name = '%s%s%s%s' % (name, Exp.RBO[0], args, Exp.RBC[0])
            return name
        # just mention
        if name == self.name:
            return name
        return '%s%s%s' % (Exp.RBO[0], name, Exp.RBC[0])

    def _encode_repeat(self):
        if self.repeat is not None:
            if self.toward is not None:
                if self.toward.repeat is not None:
                    return None
            return self.repeat


class UserDefinedMethod(Method):

    def __init__(self, name=None):
        super().__init__(name)
        self.is_method_defined = True

    def has_attr(self, name: str):
        if self.toward is not None:
            if self.toward.has_attr(name):
                return True
        return False

    def copy(self, recursive: bool = False):
        new_var = self.__class__()
        new_var.name = self.name
        new_var.toward = self.toward.copy() if self.toward is not None else None
        args_new = [arg.copy() for arg in self.args]
        for arg in args_new:
            new_var.toward.replace(arg.name, arg)
        new_var.args = args_new
        new_var.repeat = self.repeat
        return new_var

    def replace(self, name: str, value=None):
        new_var = self.copy()
        new_var.toward = new_var._replace(new_var.toward, name, value)
        return new_var

    def encode(self, stack_called=None):
        stack_called = self._ensure_stack_not_none(stack_called)
        name = self.name
        # has repeat
        args = [arg.name for arg in self.args]
        stack_called = stack_called.union(set(args))
        args += [self._encode(self.toward, stack_called)]
        name = '%s%s%s%s' % (name, Exp.RBO[0], ','.join(args), Exp.RBC[0])
        if self.repeat is not None:
            name = '%s%s%s%s%s' % (Exp.RBO[0], name, Exp.MUL[0], self.repeat.encode(stack_called), Exp.RBC[0])
        return name


def Builtins(method: str):
    func = Method(method)
    func.is_builtins = True
    return func
