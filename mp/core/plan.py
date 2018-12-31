from mp.core import attribute as attr
from mp.core import builtins as _builtins
from mp.core import data
from mp.core import framework
from mp.core.error import BaseError, RequiredError, TooMuchOrLessArguments
from mp.core.expression import Expression as Exp
from mp.core.graph import Graph
from mp.core.io import IO


class Plan:
    BUILTINS = _builtins
    CLASS_IO = IO

    MAP_NUM_TYPE = framework.MAP_NUM_TYPE

    def __init__(self, dir_process: str, message_to_data):
        self.code_to_data = message_to_data
        self.attr = attr.AttrDict()
        self.io = self.CLASS_IO(dir_process)
        self.graph = Graph()
        # Manages events for built-in methods.
        self.event = Exp.EVENT

    # execute along IO
    def execute(self):
        try:
            # (save, delete) files
            for var_name, var, value, value_raw in self._get_wait_list(self.graph.ios):
                self.io.set(var_name, value)
            # (print) files
            for var_name, var, value, value_raw in self._get_wait_list(self.graph.prints):
                self.print_var(var, value_raw)
        # if error : finish
        except BaseError as e:
            self.graph.clear()
            raise e
        self.graph.clear()

    # find method in builtins
    @classmethod
    def find_method(cls, name: str, find_hidden: bool = True):
        method = Exp.EVENT.find_unique(name, find_hidden)
        if method is not None:
            fixed = method.fixed
            method = Exp.EVENT.delegate(name, find_hidden)
            return method, fixed
        return None, None

    def _get_wait_list(self, wait_list):
        while len(wait_list) > 0:
            var_name, append = wait_list.popitem(last=False)
            # save
            if append:
                var = self.graph.vars[var_name]
                value = self._execute_recursive(var)
                value_raw = value.get_value()
            # delete
            else:
                var = None
                value = None
                value_raw = None
            yield var_name, var, value, value_raw

    # execute recursively along IO
    def _execute_recursive(self, toward: data.Variable):
        # echo
        if toward is None:
            return None
        # if required
        if toward.is_required:
            var = self._find_variable(toward)
            return var
        # is variable
        if toward.is_variable:
            return self._execute_variable(toward)
        # is constant
        if toward.is_constant:
            return self._execute_constant(toward)
        # is slicing
        if toward.is_indices:
            return self._execute_indexed(toward)
        # is transpose
        if toward.is_transpose:
            return self._execute_transpose(toward)
        # is view
        if toward.is_view:
            return self._execute_view(toward)
        # is tuple
        if toward.is_tuple:
            return self._execute_tuple(toward)
        # is operator
        if toward.is_operator:
            return self._execute_operator(toward)
        # is user-defined method
        if toward.is_method_defined:
            raise RequiredError(toward.name)
        # is method
        if toward.is_method:
            return self._execute_method(toward)
        raise NotImplementedError

    def _execute_variable_modify(self, var, toward):
        var.toward = self._execute_recursive(toward.toward)
        var.code = toward.encode()
        var.is_data = toward.is_data
        return var

    def _execute_variable_point(self, var, toward):
        toward.is_pointer = False
        # find file first
        try:
            var = self._find_variable(toward)
        # file not exist
        except RequiredError:
            self._execute_variable_modify(var, toward)

    def _execute_variable(self, toward: data.Variable):
        var = self.attr[toward.name]
        # load ahead
        if toward.is_pointer:
            self._execute_variable_point(var, toward)
        # if changed or not data
        if toward.toward is not None:
            if toward.encode() != var.code or not var.is_data:
                self._execute_variable_modify(var, toward)
        return var

    def _execute_constant(self, toward: data.Constant):
        # unsupported type
        if toward.num_type not in self.MAP_NUM_TYPE.keys():
            raise SyntaxError(toward.num_type)
        # create new tensor object
        value = self._new_const(toward)
        const = attr.AttrConst(value)
        return const

    def _execute_operator_modify(self, toward):
        var = self.attr[toward.sub]
        # reuse
        if var.reusable:
            return var
        var.value = self._execute_recursive(toward.obj)
        return var

    def _execute_operator(self, toward: data.Operator):
        # substitute
        if toward.op in Exp.IS:
            return self._execute_operator_modify(toward)
        # the others
        args = attr.AttrTuple([toward.sub, toward.obj, toward.step, *toward.args], self._execute_recursive)
        op = attr.AttrOP(toward.op, args)
        return op

    def _execute_indexed(self, toward: data.Indexed):
        return self._execute_shell(toward, attr.AttrIndexed)

    def _execute_transpose(self, toward: data.Transpose):
        return self._execute_shell(toward, attr.AttrTranspose)

    def _execute_view(self, toward: data.Transpose):
        return self._execute_shell(toward, attr.AttrView)

    def _execute_shell(self, toward: data.Shell, attribute_type):
        sub = self._execute_recursive(toward.sub)
        args = attr.AttrTuple(toward.args, self._execute_recursive)
        op = attribute_type(sub, args)
        return op

    def _execute_tuple(self, toward: data.Tuple):
        return attr.AttrTuple(toward.args, self._execute_recursive)

    @classmethod
    def _execute_method_update_repeat(cls, repeat_old, repeat_new):
        if repeat_old is None:
            return repeat_new
        if repeat_new is None:
            return repeat_old
        # multiply repeat numbers
        return data.Operator(Exp.MUL[0], repeat_old, repeat_new)

    def _execute_method_delegate(self, toward):
        name = toward.name
        toward_origin = toward
        repeat = toward.repeat
        while toward.toward is not None and not toward.is_method_defined:
            toward = toward.toward
            if name.startswith(Exp.CODE_CONST):
                name = toward.name
            repeat = self._execute_method_update_repeat(repeat, toward.repeat)
        # if builtins
        if toward.is_builtins:
            method, fixed = self.find_method(toward.name, find_hidden=False)
            args = attr.AttrTuple(toward_origin.args, self._execute_recursive)
            kwargs = attr.AttrDict(toward_origin.kwargs, self._execute_recursive)
            repeat = self._execute_recursive(repeat)
            return attr.AttrMethod(self, name, method, toward_origin, args, kwargs, fixed, repeat)
        # if user-defined methods
        if toward.is_method_defined:
            return self._execute_method_defined(toward, name, toward_origin.args, repeat)
        # undefined error
        raise RequiredError(toward.name)

    def _execute_method(self, toward: data.Method):
        # point method
        if toward.is_method_delegate:
            return self._execute_method_delegate(toward)
        # call method
        method = self._execute_method_delegate(toward)
        return method

    def _execute_method_defined(self, toward: data.UserDefinedMethod, name, args, repeat):
        # check sizeof args
        if toward.args_min > len(args) or toward.args_max < len(args):
            raise TooMuchOrLessArguments(name, toward.args_min, len(args), int(toward.args_min != toward.args_max))
        args = attr.AttrTuple(args, self._execute_recursive)
        # add placeholders
        placeholders = attr.AttrTuple(toward.args, self._execute_recursive)
        # call method
        method = self._execute_recursive(toward.toward)
        method.code = toward.toward.encode()
        # add repeat
        repeat = self._execute_recursive(repeat)
        # create iteration
        method = attr.AttrIteration(toward.name, method, toward, placeholders, args, repeat)
        return method

    # find variable from file-system
    def _find_variable(self, toward):
        name = toward.name
        # if not variable
        if name is None:
            raise RequiredError('None')
        value = self.io.get(name)
        # not found
        if value is None:
            raise RequiredError(name)
        # if graph
        if type(value) is str:
            # set 'self'
            self.graph.push_self(name)
            # load script
            values = list(self.code_to_data(value))
            for value in values:
                self.push(value)
            # remove 'self'
            self.graph.pop_self()
            # just script
            if toward.toward is None:
                return attr.AttrConst(False)
            var = self._execute_recursive(toward)
            return var
        # if binary
        elif type(value) is data.Constant:
            toward.toward = value
            var = self._execute_recursive(toward)
            return var
        raise NotImplementedError

    # return new constant
    def _new_const(self, toward):
        raise NotImplementedError

    # update graph
    def push(self, value):
        # has query
        if value is not None:
            value.update_graph(self.graph)

    @classmethod
    def print_var(cls, var, value):
        print('%s = %s' % (var.symbol, value))

    @classmethod
    def get_builtin_methods(cls):
        return [t for t in dir(cls.BUILTINS) if hasattr(getattr(cls.BUILTINS, t), '_method')], cls.BUILTINS
