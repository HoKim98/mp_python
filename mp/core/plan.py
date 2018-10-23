from mp.core import attribute as _attribute
from mp.core import builtins as _builtins
from mp.core import data
from mp.core.error import BaseError, RequiredError, TooMuchOrLessArguments
from mp.core.expression import Expression as Exp
from mp.core.graph import Graph
from mp.core.io import IO


class Plan:
    ATTR = _attribute
    BUILTINS = _builtins
    CLASS_IO = IO

    def __init__(self, dir_process: str, message_to_data):
        self.code_to_data = message_to_data
        self.attr = self.ATTR.AttrDict()
        self.io = self.CLASS_IO(dir_process)
        self.graph = Graph()

    # execute along IO
    def execute(self):
        # self.graph.lock_point = True
        try:
            while len(self.graph.ios) > 0:
                var_name, append = self.graph.ios.popitem()
                # save
                if append:
                    var = self.graph.vars[var_name]
                    value = self._execute_recursive(var)
                    value.get_value()
                # delete
                else:
                    value = None
                self.io.set(var_name, value)
        # if error : finish
        except BaseError as e:
            self.graph.clean()
            raise e
        self.graph.lock_point = False
        self.graph.clean()

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
        if type(toward) is data.Variable:
            return self._execute_variable(toward)
        # is constant
        if type(toward) is data.Constant:
            return self._execute_constant(toward)
        # is operator
        if type(toward) is data.Operator:
            return self._execute_operator(toward)
        # is slicing
        if type(toward) is data.Indexed:
            return self._execute_indexed(toward)
        # is view
        if type(toward) is data.View:
            return self._execute_view(toward)
        # is method
        if type(toward) is data.Method:
            return self._execute_method(toward)
        # is user-defined method
        if type(toward) is data.UserDefinedMethod:
            raise RequiredError(toward.name)
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
        if toward.num_type not in self.ATTR.map_num_type.keys():
            raise SyntaxError(toward.num_type)
        # create new array object
        value = self._new_const(toward)
        const = self.ATTR.AttrConst(toward.encode(), value)
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
        args = self.ATTR.AttrList([toward.sub, toward.obj, toward.step, *toward.args], self._execute_recursive)
        op = self.ATTR.AttrOP(toward.op, args)
        return op

    def _execute_indexed(self, toward: data.Indexed):
        sub = self._execute_recursive(toward.sub)
        args = self.ATTR.AttrList(toward.args, self._execute_recursive)
        op = self.ATTR.AttrIndexed(sub, args)
        return op

    def _execute_view(self, toward: data.View):
        args = self.ATTR.AttrList(toward.args, self._execute_recursive)
        sub = self._execute_recursive(toward.sub)
        op = self.ATTR.AttrView(sub, args)
        return op

    def _execute_method_fix(self, toward):
        if toward is not None:
            return self._execute_recursive(toward)
        return None

    def _execute_method_update_repeat(self, repeat_old, repeat_new):
        if repeat_old is None:
            return repeat_new
        if repeat_new is None:
            return repeat_old
        # multiply repeat numbers
        args = self.ATTR.AttrList([repeat_old, repeat_new])
        return self.ATTR.AttrOP(Exp.MUL[0], args)

    def _execute_method_delegate(self, toward):
        toward_origin = toward
        repeat = self._execute_method_fix(toward.repeat)
        while toward.toward is not None and not toward.is_method_defined:
            toward = toward.toward
            repeat_new = self._execute_method_fix(toward.repeat)
            repeat = self._execute_method_update_repeat(repeat, repeat_new)
        # if builtins
        if toward.is_builtins:
            method = Exp.BUILTINS[toward.name]
            args = self.ATTR.AttrList(toward_origin.args, self._execute_recursive)
            return self.ATTR.AttrMethod(toward_origin.name, method, toward_origin, args, repeat)
        # if user-defined methods
        if toward.is_method_defined:
            return self._execute_method_defined(toward, toward_origin.name, toward_origin.args)
        # undefined error
        raise RequiredError(toward.name)

    def _execute_method(self, toward: data.Method):
        # point method
        if toward.is_method_delegate:
            return self._execute_method_delegate(toward)
        # call method
        method = self._execute_method_delegate(toward)
        return method

    def _execute_method_defined(self, toward: data.UserDefinedMethod, name, args):
        # check sizeof args
        if len(toward.args) != len(args):
            raise TooMuchOrLessArguments(name, len(toward.args), len(args))
        # replace with copy
        toward = toward.copy()
        for arg_from, arg_to in zip(args, toward.args):
            arg_to.toward = arg_from
        # call method
        method = self._execute_recursive(toward.toward)
        method.code = toward.toward.encode()
        return method

    # find variable from file-system
    def _find_variable(self, toward):
        name = toward.symbol
        # if not variable
        if name is None:
            raise RequiredError('None')
        value = self.io.get(name)
        # not found
        if value is None:
            raise RequiredError(name)
        # if graph
        if type(value) is str:
            values = list(self.code_to_data(value))
            for value in values:
                self.push(value)
            # just script
            if toward.toward is None:
                var = data.Constant(self.graph.new_name(), 'b', False)
                return self.ATTR.AttrConst(var.encode(), var)
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
    def get_builtin_methods(cls):
        return [t for t in dir(cls.BUILTINS) if not t.startswith('_')], cls.BUILTINS
