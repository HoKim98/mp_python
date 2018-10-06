from core import error
from core.expression import Expression as Exp


class Token:

    TYPE_BINARY = 0
    TYPE_OPERATOR = 1
    TYPE_NUMBER = 2
    TYPE_VARIABLE = 3
    TYPE_TUPLE = 4
    TYPE_RANGE = 5
    TYPE_SIZEOF = 6
    TYPE_POINTER = 7

    def __init__(self, name: str, data_type: int, *args, toward=None):
        self.name = name
        self.data_type = data_type
        self.args = args
        self.toward = toward

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
    def from_number(cls, num_type, value):
        return Token(num_type, cls.TYPE_NUMBER, value)

    @classmethod
    def from_var(cls, name, *list_indices):
        return Token(name, cls.TYPE_VARIABLE, *list_indices)

    @classmethod
    def from_pointer(cls, name=''):
        return Token(name, cls.TYPE_POINTER)

    @classmethod
    def from_tuple(cls, *data):
        return Token(Exp.TUPLE, cls.TYPE_TUPLE, *data)

    @classmethod
    def from_range(cls, range_type, *data):
        return Token(range_type, cls.TYPE_RANGE, *data)

    @classmethod
    def call_method(cls, var, operands):
        # arguments
        if len(var.args) == 0:
            if len(operands) >= 1:
                # arguments must be tuple
                operand = operands[0].range_to_tuple()
                if operands[0].is_indices:
                    var.args = operand.args
                else:
                    var.args = [operand]
            if len(operands) == 1:
                return True, operands
            # chain shells
            operands = operands[1:]
        return False, operands

    def update_graph(self, graph):
        self.update_graph_recursive(graph)
        return graph

    def update_graph_recursive(self, graph):
        if self.data_type == self.TYPE_OPERATOR:
            operands = list()
            for arg in self.args:
                if arg is None:
                    operands.append(None)
                    continue
                operand = arg.update_graph_recursive(graph)
                operands.append(operand)
            # (save, delete) files
            if self.name in Exp.SAVE + Exp.DELETE:
                operate = graph.save if self.name in Exp.SAVE else graph.delete
                if len(operands) == 1:
                    operate(None, operands[0])
                else:
                    root = operands[0]
                    for f in operands[1:]:
                        operate(root, f)
                return None
            # (return, iterate) values
            elif self.name in Exp.NEXT:
                pass  # TODO next 구문을 어떻게 구현할 지 다시한번 생각할 것.
            # indices
            elif self.name in Exp.IDX:
                begin = operands[0]
                end = operands[1] if len(operands) == 2 else None
                return graph.slice(begin, end)
            # view
            elif self.name in Exp.SHELL_AA:
                return graph.view(*operands)
            # =
            elif self.name in Exp.IS:
                begin = operands[0]
                end = operands[1]
                # 'tuple = tuple'
                if begin.is_indices and end.is_indices:
                    if len(begin.args) != len(end.args):
                        raise error.SyntaxError(self.name)
                    for sub, obj in zip(begin.args, end.args):
                        graph.operate(self.name, sub, obj)
                    return operands[0]
                else:
                    return graph.operate(self.name, begin, end)
            # just operators
            else:
                return graph.operate(self.name, *operands)
        elif self.data_type == self.TYPE_NUMBER:
            return graph.alloc(self.name, self.args[0])
        elif self.data_type == self.TYPE_VARIABLE:
            operands = list()
            for arg in self.args:
                operand = arg.update_graph_recursive(graph)
                operands.append(operand)
            # callable
            var = graph.find(self.name)
            # is method or builtins
            if var.is_method:
                no_more_args, operands = self.call_method(var, operands)
                if no_more_args:
                    return var
            # refer to method or builtins
            elif var.toward is not None:
                if var.toward.is_method:
                    var.toward = var.toward.copy()
                    no_more_args, operands = self.call_method(var.toward, operands)
                    if no_more_args:
                        return var
            # the others
            for operand in operands:
                # if not tuple or indices
                if not (operand.is_indices or operand.is_view):
                    operand = graph.indices(operand)
                sub = operand.sub
                if sub.is_required:
                    operand.sub = var
                    var = operand
                    continue
            return var
        elif self.data_type == self.TYPE_TUPLE:
            operands = list()
            for arg in self.args:
                operand = arg.update_graph_recursive(graph)
                operands.append(operand)
            return graph.indices(*operands)

    def __repr__(self):
        return self.name + '{ ' + ', '.join([repr(data) for data in self.args]) + ' }'
