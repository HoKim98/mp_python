import os

from core import error
from core.token import Token
from core.error import IOError
from core.expression import Expression as Exp
from core.plan import Plan

from utils import interactive as _interactive


class TokenTree(list):
    def __init__(self, parent, head):
        super().__init__()
        self.parent = parent
        self.head = head
        self.pointer = 0

    @classmethod
    def _is_number(cls, token_cat):
        # test-integer using python trick
        try:
            return int(token_cat), Exp.INT_DEFAULT
        except ValueError:
            pass
        # test-real using python trick
        try:
            return float(token_cat), Exp.FLOAT_DEFAULT
        except ValueError:
            pass
        # find type
        try:
            token_cat = token_cat.lower()
            for t_name, t_func in zip([Exp.INT, Exp.FLOAT], [int, float]):
                try:
                    idx = token_cat.index(t_name)
                    try:
                        num = t_func(token_cat[:idx])
                    except ValueError:
                        try:
                            num = float(token_cat[:idx])
                            num = t_func(num)
                        except ValueError:
                            continue
                    n_bits = int(token_cat[idx+1:])
                    if n_bits in [8, 16, 32, 64]:
                        return num, '%s%d' % (t_name, n_bits)
                except ValueError:
                    continue
        except ValueError:
            pass
        return 0, ''

    def tokenize(self):
        if len(self) < self.pointer:
            self.pointer = len(self)
            return

        tokens = self[self.pointer:]
        try:
            token_cat = ''.join(tokens)
        except TypeError:
            return
        del self[self.pointer:]

        # is numeric
        num, type_num = self._is_number(token_cat)
        if len(type_num) > 0:
            new_object = TokenTree(self, Exp.NUMBER)
            new_object += [num, type_num]
            self.append(new_object)
            self.pointer = len(self)
        # is variable or tuple
        elif len(tokens) > 0:
            # remove unnecessary token
            while len(self) >= 1:
                if self[0].head == Exp.VARIABLE:
                    if len(self[0]) == 0:
                        del self[0]
                        continue
                break
            tokens = token_cat.split(Exp.DOT)
            new_object = TokenTree(self, Exp.VARIABLE)
            new_object += tokens
            self.append(new_object)
            self.pointer = len(self)

    def close(self, token_end: str):
        if self.head in Exp.Tokens_Open and token_end in Exp.Tokens_Close:
            shell = self.head + token_end
            if shell not in Exp.Tokens_Shell:
                raise error.SyntaxError(shell[-1])
            if shell in Exp.SHELL_RR and len(self) == 1 and self[0].head in Exp.Tokens_Order:
                last_object = self[0]
                del self[0]
                self.__iadd__(last_object)
                self.head = last_object.head
            else:
                self.head = shell

    def append(self, target):
        super().append(target)
        if type(target) is TokenTree:
            self.pointer += 1

        # check subject is numeric
        if self.head == Exp.VARIABLE and len(self) == 1:
            if type(target) is str:
                if len(self._is_number(self[0])[1]) > 0:
                    raise error.SyntaxError(self[0])

    def check_sizeof(self):
        if self.head in [Exp.NUMBER, Exp.VARIABLE, ]:
            pass
        elif self.head in ['t'] + Exp.Tokens_Shell:
            pass
        elif self.head in Exp.IDX:
            if 1 <= len(self) <= 2:
                pass
            else:
                raise error.SyntaxError(self.head)
        elif len(self) != 2:
            raise error.SyntaxError(self.head)
        for token in self:
            if type(token) is TokenTree:
                token.check_sizeof()

    def to_data(self):
        # separate indices from range
        if self.head in Exp.SHELL_RR:
            # not (2 <= len(self) <= 3):
            if not len(self) == 2:
                self.head = Exp.TUPLE

        # is number
        if self.head == Exp.NUMBER:
            return Token.from_number(self[1], self[0])
        # is variable
        if self.head == Exp.VARIABLE:
            # reassemble name
            name = self[0]
            i = 1
            while i < len(self):
                name_next = self[i]
                if type(name_next) is str:
                    name = '%s.%s' % (name, name_next)
                    i += 1
                else:
                    break
            # stack indices
            list_indices = []
            for indices in self[i:]:
                indices = indices.to_data()
                # escape shell
                while True:
                    if indices.name in Exp.SHELL_RR:
                        indices.name = Exp.TUPLE
                        indices.data_type = Token.TYPE_TUPLE
                        if len(indices.args) != 1:
                            break
                        indices = indices.args[0]
                        continue
                    if indices.data_type != Token.TYPE_TUPLE:
                        break
                    if len(indices.args) != 1:
                        break
                    indices = indices.args[0]
                list_indices.append(indices)
            return Token.from_var(name, *list_indices)
        # is tuple
        if self.head == Exp.TUPLE:
            data = [token.to_data() for token in self]
            return Token.from_tuple(*data)
        # is operator
        if self.head in Exp.Tokens_Order.keys():
            data = [token.to_data() for token in self]
            return Token.from_operator(self.head, *data)
        # is range
        if self.head in Exp.Tokens_Range:
            # if not (2 <= len(self) <= 3):
            if not len(self) == 2:
                raise error.SyntaxError(self.head[0])
            data = [token.to_data() for token in self]
            return Token.from_range(self.head, *data)

    def __repr__(self):
        return self.head + '{ ' + ', '.join([repr(token) for token in self]) + ' }'


class Interpreter:
    VERSION = '0.1'

    def __init__(self, dir_process: str = './', plan=None):
        self.dir_process = os.path.join(dir_process)
        plan = Plan if plan is None else plan
        self.plan = plan(dir_process, self.code_to_data)
        self._init_builtin_methods()

    def execute_script(self, var_name: str):
        path = self.plan.io.get_path(var_name, self.dir_process)
        path = '%s.%s' % (path, Exp.EXTENSION_SOURCE)
        if not os.path.exists(path):
            raise IOError(path)
        with open(path, 'r') as f:
            msg = f.read()
            self(msg)

    @classmethod
    def add_module(cls, module_name: str, module_func):
        Exp.BUILTINS[module_name] = module_func

    def _init_builtin_methods(self):
        external_methods, modules = self.plan.get_builtin_methods()
        for module_name in external_methods:
            module_func = getattr(modules, module_name)
            Exp.BUILTINS[module_name] = module_func
        if Exp.ARRAY not in Exp.BUILTINS.keys():
            raise NotImplementedError

    @classmethod
    def _scanner(cls, line: str):
        result = []

        token = ''
        test_d = 0
        for c in line:
            if token + c in Exp.Signs_DoubleTriple:
                if test_d != 2:
                    if len(token) >= 1:
                        result.append(token)
                result.append(token + c)
                test_d = 0
                token = ''

            elif token + c in Exp.Signs_DoubleDouble:
                if test_d != 1:
                    if len(token) >= 1:
                        result.append(token)
                test_d = 2
                token += c

            elif c in Exp.Signs_DoubleSingle:
                if len(token) >= 1:
                    result.append(token)
                test_d = 1
                token = c

            elif c in Exp.Signs:
                if len(token) >= 1:
                    result.append(token)
                    token = ''
                result.append(c)

            elif c in Exp.INDENT:
                if len(token) >= 1:
                    result.append(token)
                    token = ''
                result.append(c)

            elif c not in Exp.Signs_All:
                if len(token) >= 1:
                    if token[-1] in Exp.Signs_All:
                        result.append(token)
                        token = ''
                token += c
        if len(token) >= 1:
            result.append(token)
        return result

    @classmethod
    def _parser(cls, tokens):
        prefixes = TokenTree(None, Exp.TUPLE)

        query = TokenTree(None, Exp.VARIABLE)
        object_attr = query
        for w in tokens:
            # comments
            if w == Exp.COMMENT:
                break

            # indents
            if w in Exp.INDENT:
                continue

            # subjects
            # check operator overlap
            if len(object_attr) == 0:
                if w in Exp.Signs_All and w not in Exp.IDX:
                    # not shell
                    if object_attr.head in Exp.Tokens_Open and w in Exp.Tokens_Open + Exp.Tokens_Close:
                        pass
                    # not variable or shell
                    elif object_attr.head in Exp.VARIABLE and w in Exp.Tokens_Open:
                        pass
                    # not unary operator (-)
                    elif w in Exp.SUB:
                        pass
                    else:
                        raise error.SyntaxError(w)
            # attribute
            if w == Exp.COMMA:
                while object_attr.head not in Exp.Tokens_Open:
                    last_object = object_attr.parent
                    # indices
                    if object_attr.head in Exp.IDX:
                        if last_object is None:
                            raise error.SyntaxError(object_attr.head)
                        object_attr.tokenize()
                        object_attr = last_object
                        break
                    # substitute
                    elif object_attr.head in Exp.Tokens_Inplace:
                        object_attr.tokenize()
                        last_object = object_attr.pop(-1)
                        new_object = TokenTree(object_attr, Exp.TUPLE)
                        new_object.append(last_object)
                        object_attr.append(new_object)
                        object_attr = new_object
                        break
                    # tuple
                    elif object_attr.head == Exp.TUPLE:
                        object_attr.tokenize()
                        break
                    # new tuple
                    elif last_object is None:
                        query = new_object = TokenTree(None, Exp.TUPLE)
                        object_attr.parent = new_object
                        new_object.append(object_attr)
                        object_attr = new_object
                        break
                    else:
                        object_attr.tokenize()
                        object_attr = last_object
                object_attr.tokenize()
            # prefixes
            elif w in Exp.Tokens_Prefix:
                # not from- prefix
                if w not in Exp.FROM:
                    if object_attr.parent is None and object_attr.head == Exp.VARIABLE:
                        if len(query) > 0:
                            prefixes.append(query)
                        prefixes.append(w)
                        prefixes.tokenize()
                        query = TokenTree(None, Exp.VARIABLE)
                        object_attr = query
                        continue
                # from- prefix
                elif object_attr.parent is None and len(object_attr) == 0:
                    prefixes.append(w)
                    prefixes.tokenize()
                    continue
                raise error.SyntaxError(w)
            # indices
            elif w in Exp.Tokens_Close:
                object_attr.tokenize()
                while object_attr.head not in Exp.Tokens_Open:
                    object_attr = object_attr.parent
                    if object_attr is None:
                        raise error.SyntaxError(w)
                object_attr.close(w)
                object_attr = object_attr.parent
                if object_attr is None:
                    raise error.SyntaxError(w)
            elif w in Exp.Tokens_Order.keys():
                # 'n'umber, 'v'ariable, 't'uple
                if w in Exp.ABSTRACT_TYPES:
                    object_attr.append(w)
                    continue
                object_attr.tokenize()
                # operator - for negative number
                if w in Exp.SUB:
                    # =
                    if len(object_attr) == 1:
                        if object_attr.head in Exp.IS:
                            object_attr.append(w)
                            continue
                    # if shell
                    if len(object_attr) == 0:
                        if object_attr.head in Exp.Tokens_Open:
                            object_attr.append(w)
                            continue
                # variable overlap
                if object_attr.head == Exp.VARIABLE and len(object_attr) == 1:
                    new_object = object_attr[0]
                    new_object.parent = object_attr.parent
                    if new_object.parent is None:
                        query = new_object
                    object_attr = new_object
                # higher order
                if Exp.Tokens_Order[object_attr.head] < Exp.Tokens_Order[w]:
                    # if shell
                    if w in Exp.Tokens_Open:
                        # check calling function
                        if object_attr.head not in [Exp.NUMBER, Exp.VARIABLE, Exp.TUPLE]:
                            if len(object_attr) == 2:
                                if object_attr[-1].head == Exp.VARIABLE:
                                    object_attr = object_attr[-1]
                        new_object = TokenTree(object_attr, w)
                        object_attr.append(new_object)
                        object_attr = new_object
                        continue
                    last_object = object_attr.pop(-1)
                    new_object = TokenTree(object_attr, w)
                    new_object.append(last_object)
                    object_attr.append(new_object)
                    object_attr = new_object
                # lower order
                else:
                    # if in shell
                    if object_attr.head in Exp.Tokens_Open:
                        # indices
                        if w in Exp.IDX:
                            last_object = TokenTree(object_attr, Exp.NUMBER)
                            last_object += [0, Exp.INT_DEFAULT]
                            if len(object_attr) > 0:
                                if object_attr[-1].head not in Exp.IDX:
                                    last_object = object_attr.pop(-1)
                        elif len(object_attr) > 0:
                            last_object = object_attr.pop(-1)
                        # overlap shell
                        elif w in Exp.Tokens_Open:
                            new_object = TokenTree(object_attr, w)
                            object_attr.append(new_object)
                            object_attr = new_object
                            continue
                        else:
                            raise error.SyntaxError(w)
                        new_object = TokenTree(object_attr, w)
                        new_object.append(last_object)
                        object_attr.append(new_object)
                        object_attr = new_object
                        continue
                    last_object = object_attr.parent
                    if last_object is None:
                        new_object = TokenTree(None, w)
                        new_object.append(object_attr)
                        object_attr.parent = new_object
                        object_attr = new_object
                        query = object_attr
                        continue
                    del last_object[-1]
                    new_object = TokenTree(last_object, w)
                    object_attr.parent = new_object
                    last_object.append(new_object)
                    new_object.append(object_attr)
                    if new_object.parent is None:
                        query = new_object
                    object_attr = new_object
            elif w[0] in Exp.Signs_DoubleSingle:
                raise error.SyntaxError(w)
            # append text
            elif object_attr.head == Exp.VARIABLE and len(object_attr) == 1:
                object_attr[0] += w
            # add content
            else:
                object_attr.append(w)
        prefixes.tokenize()
        object_attr.tokenize()
        # variable overlap
        if object_attr.head == Exp.VARIABLE and len(object_attr) == 1:
            last_object = object_attr[0]
            del object_attr[0]
            object_attr += last_object
            object_attr.head = last_object.head

        # check size of operators
        prefixes.check_sizeof()
        query.check_sizeof()

        # check prefixes
        prefix_from_pair = True
        prefixes_new = TokenTree(None, Exp.TUPLE)
        for token in prefixes:
            if token.head != Exp.VARIABLE:
                raise error.SyntaxError(token[0])
            # has 'from'
            if token[0] in Exp.FROM:
                prefix_from_pair = False
                if len(prefixes_new) != 0:
                    raise error.SyntaxError(token[0])
            elif token[0] in Exp.Tokens_Prefix:
                prefix_from_pair = True
                if len(prefixes_new) != 0:
                    if prefixes_new[-1][0] in Exp.Tokens_Prefix:
                        raise error.SyntaxError(token[0])
            if len(prefixes_new) > 3:
                raise error.SyntaxError(token[0])
            prefixes_new.append(token)
        if not prefix_from_pair:
            raise error.SyntaxError(Exp.FROM[0])
        prefixes = prefixes_new

        return prefixes, query

    @classmethod
    def _semantic_analysis(cls, prefixes, query):
        # no query
        if len(query) == 0:
            return None

        # analyse prefixes
        prefix_from = None
        save_files = 0
        next_iters = 0
        delete_files = 0
        prefixes_iter = iter(prefixes)
        for token in prefixes_iter:
            if type(token[0]) is not str:
                raise error.SyntaxError(token)
            token = token[0]
            # save files
            if token in Exp.FROM:
                prefix_from = next(prefixes_iter)
                # prefix_from = Data.from_var(prefix_from[0])
                prefix_from = Token.from_var(''.join(prefix_from))
            elif token in Exp.SAVE:
                save_files += 1
            # iteration
            elif token in Exp.NEXT:
                next_iters += 1
            # delete files
            elif token in Exp.DELETE:
                delete_files += 1
            # check overlap
            if save_files + next_iters + delete_files >= 2:
                raise error.SyntaxError(token)

        query = query.to_data()

        # (save, delete) files
        for op, test, func in zip([Exp.SAVE[0], Exp.DELETE[0]],
                                  [save_files, delete_files],
                                  [Token.from_save, Token.from_delete]):
            if not test:
                continue
            if query.data_type == Token.TYPE_VARIABLE:
                return func(prefix_from, query)
            elif query.data_type == Token.TYPE_TUPLE:
                return func(prefix_from, *query.args)
            else:
                raise error.SyntaxError(op)
        # (iterate) values
        for op, test in zip([Exp.NEXT[0]], [next_iters]):
            if not test:
                continue
            if prefix_from is not None:
                raise error.SyntaxError(op)
            if query.data_type == Token.TYPE_VARIABLE:
                return Token.from_operator(op, query)
            elif query.data_type == Token.TYPE_TUPLE:
                return Token.from_operator(op, *query.args)
            else:
                raise error.SyntaxError(op)
        # just data
        return query

    def begin_interactive(self):
        _interactive(self)

    def code_to_data(self, message: str):
        lines = message.split(Exp.NEXTLINE)
        for line in lines:
            tokens = self._scanner(line)
            prefixes, query = self._parser(tokens)
            data = self._semantic_analysis(prefixes, query)
            yield data

    def __call__(self, message: str, lazy_execute: bool = True):
        for data in self.code_to_data(message):
            self.plan.push(data)
            if not lazy_execute:
                self.plan.execute()
        if lazy_execute:
            self.plan.execute()
