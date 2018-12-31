from mp.core.error import SyntaxError
from mp.core.expression import Expression as Exp


class Token:

    TYPE_BINARY = 0
    TYPE_OPERATOR = 1
    TYPE_NUMBER = 2
    TYPE_VARIABLE = 3
    TYPE_TUPLE = 4
    TYPE_SIZEOF = 5

    def __init__(self, name: str, data_type: int, *args):
        self.name = name
        self.data_type = data_type
        self.args = args

    @classmethod
    def from_binary(cls, raw):
        pass

    @classmethod
    def from_operator(cls, operator, *args):
        operator = str(operator)
        return Token(operator, cls.TYPE_OPERATOR, *args)

    @classmethod
    def from_save(cls, dir_from, *files):
        return Token(Exp.SAVE[0], cls.TYPE_OPERATOR, dir_from, *files)

    @classmethod
    def from_delete(cls, dir_from, *files):
        return Token(Exp.DELETE[0], cls.TYPE_OPERATOR, dir_from, *files)

    @classmethod
    def from_print(cls, dir_from, *files):
        return Token(Exp.PRINT[0], cls.TYPE_OPERATOR, dir_from, *files)

    @classmethod
    def from_number(cls, num_type, value):
        return Token(num_type, cls.TYPE_NUMBER, value)

    @classmethod
    def from_var(cls, name):
        return Token(name, cls.TYPE_VARIABLE)

    @classmethod
    def from_tuple(cls, *data):
        return Token(Exp.TUPLE, cls.TYPE_TUPLE, *data)

    @classmethod
    def from_range(cls, range_type, *data):
        return Token(range_type, cls.TYPE_OPERATOR, *data)

    def update_graph(self, graph):
        self.update_graph_recursive(graph)
        return graph

    def update_graph_recursive(self, graph):
        if self.data_type == self.TYPE_OPERATOR:
            operands = self._get_operands(self.args, graph)
            # (save, delete, print) files
            if self.name in Exp.SAVE + Exp.DELETE + Exp.PRINT:
                # operation mapping
                if self.name in Exp.SAVE:
                    operate = graph.save
                elif self.name in Exp.SAVE:
                    operate = graph.delete
                elif self.name in Exp.PRINT:
                    operate = graph.print
                else:
                    raise NotImplementedError
                # case
                if len(operands) == 1:
                    operate(None, operands[0])
                else:
                    root = operands[0]
                    for f in operands[1:]:
                        operate(root, f)
                return None
            # slice
            elif self.name in Exp.IDX:
                return self._index(operands, graph)
            # transpose
            elif self.name in Exp.SHELL_AA:
                return graph.transpose(*operands)
            # call method or indices
            elif self.name in Exp.SHELL_RR:
                # call method
                sub = operands[0]
                if sub.is_method_delegate:
                    # if user-defined method
                    if sub.is_method_defined and sub.toward is None:
                        return self._user_defined_method(sub, operands, graph)
                    # if user-defined method
                    # or just to call
                    return self._call_method(sub, operands, graph)
                # indices
                return graph.indices(*operands)
            # view
            elif self.name in Exp.SHELL_SS:
                return graph.view(*operands)
            # if repeat call
            elif self.name in Exp.MUL:
                # repeat call
                sub = operands[0]
                if sub.is_method_delegate:
                    return self._repeat_call(sub, operands, graph)
                # normal multiply
                else:
                    return graph.operate(self.name, *operands)
            # just operators
            else:
                return graph.operate(self.name, *operands)
        # constant
        elif self.data_type == self.TYPE_NUMBER:
            return graph.alloc(self.name, self.args[0])
        # variable or method (builtins)
        elif self.data_type == self.TYPE_VARIABLE:
            return graph.find(self.name)
        # tuple
        elif self.data_type == self.TYPE_TUPLE:
            operands = self._get_operands(self.args, graph)
            return graph.tuple(*operands)

    def _user_defined_method(self, sub, operands, graph):
        var = sub
        if len(operands) == 1:
            raise SyntaxError(var.name)
        args, toward = operands[1:-1], operands[-1]
        var.toward = toward
        # put into placeholder
        args_new = []
        for arg_to in args:
            var.args_max += 1
            # create a parameter
            parameter = self._new_parameter(arg_to, graph)
            # replace global variable with it
            args_new.append(parameter)
            var.toward.replace(arg_to.symbol, parameter)
            # if required
            if parameter.is_required:
                graph.set_placeholder(parameter)
                var.args_min += 1
                if var.args_min != var.args_max:
                    raise SyntaxError(parameter.symbol)
        var.args = args_new
        if var.toward.is_variable:
            var.toward = self._new_parameter(var.toward, graph)
        return var

    def _call_method(self, sub, operands, graph):
        var = graph.point_method(graph.new_name(), sub)
        var.args = operands[1:]
        var.is_data = True
        var.is_method_delegate = False
        # if method defined
        method_base = self._find_method_base(var.toward)
        if method_base.is_method_defined:
            self._replace_keywords(method_base.args, var.args)
        # the others
        else:
            self._detach_keywords(var)
        return var

    def _repeat_call(self, sub, operands, graph):
        var = graph.point_method(graph.new_name(), sub)
        repeat = operands[1]
        # double multiply
        if var.repeat is not None:
            repeat = graph.operate(self.name, var.repeat, repeat)
        var.repeat = repeat
        return var

    @classmethod
    def _find_method_base(cls, method):
        while method is not None:
            if method.toward is None or method.is_method_defined:
                return method
            method = method.toward
        raise NotImplementedError

    @classmethod
    def _replace_keywords(cls, type_params, real_params):
        # is placeholder?
        def check_placeholder(idx):
            if type_params[idx].toward.is_placeholder:
                raise SyntaxError(arg_real.symbol)

        # replace from 'idx_from' to 'idx_to' safely
        def save_replace(idx_from, idx_to):
            check_placeholder(idx_to)
            real_params[idx_to] = type_params[idx_from].toward

        # expand list as needed
        def expand():
            while len(real_params) <= idx_type:
                check_placeholder(len(real_params))
                real_params.append(type_params[len(real_params)].toward)

        # execute replacing
        for idx_type, arg_type in enumerate(type_params):
            for idx_real, arg_real in enumerate(real_params):
                if arg_type.symbol == arg_real.symbol:
                    tmp = arg_real.toward
                    save_replace(idx_real, idx_real)
                    expand()
                    real_params[idx_type] = tmp

    def _detach_keywords(self, var):
        kwargs_begin = None
        for idx, (arg, arg_ast) in enumerate(zip(var.args, self.args[1:])):
            if arg_ast.name in Exp.IS:
                var.kwargs[arg.symbol] = arg.toward
                kwargs_begin = kwargs_begin or idx
            elif kwargs_begin is not None:
                raise SyntaxError(arg.symbol)
        var.args = var.args[:kwargs_begin]

    @classmethod
    def _new_parameter(cls, var, graph):
        new_name = '%s%s%s%s' % (Exp.CODE_PARAM, graph.new_name()[1:], Exp.DOT, var.symbol)
        new_var = graph.find(new_name)
        new_var.toward = var.toward
        return new_var

    @classmethod
    def _index(cls, operands, graph):
        start = operands[0]
        stop = operands[1] if len(operands) >= 2 else None
        step = operands[2] if len(operands) == 3 else None
        start = start if bool(start) else None
        stop = stop if bool(stop) else None
        return graph.slice(start, stop, step)

    @classmethod
    def _get_operands(cls, args, graph):
        operands = list()
        for arg in args:
            if arg is None:
                operands.append(None)
                continue
            operand = arg.update_graph_recursive(graph)
            operands.append(operand)
        return operands

    def __repr__(self):
        return self.name + '{ ' + ', '.join([repr(data) for data in self.args]) + ' }'
