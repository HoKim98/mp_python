import os

from mp.core import error
from mp.core.token import Token
from mp.core.event import Event
from mp.core.expression import Expression as Exp
from mp.core.plan import Plan

from mp.monitor import StdMonitor

from mp.utils import interactive as _interactive


class TokenTree(list):
    def __init__(self, parent, head):
        super().__init__()
        self.parent = parent
        self.head = head
        self.pointer = 0
        # for indexing (:)
        self.breakpoint = 0
        self.has_subject = False

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
            for t_name, t_func in zip([Exp.BOOL, Exp.INT, Exp.FLOAT], [bool, int, float]):
                try:
                    idx = token_cat.index(t_name)
                    try:
                        # is boolean
                        if t_name == Exp.BOOL:
                            num = t_func(int(token_cat[:idx]))
                        # is numeric
                        else:
                            num = t_func(token_cat[:idx])
                    except ValueError:
                        try:
                            num = float(token_cat[:idx])
                            num = t_func(num)
                        except ValueError:
                            continue
                    # is boolean
                    if t_name == Exp.BOOL:
                        return num, '%s' % t_name
                    # is numeric
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
                        self.pop(0)
                        continue
                break
            tokens = token_cat.split(Exp.DOT)
            tokens = [token.strip() for token in tokens]
            new_object = TokenTree(self, Exp.VARIABLE)
            new_object += tokens
            self.append(new_object)
            self.pointer = len(self)

    def close(self, token_end: str):
        # make shell shape
        shell = self.head + token_end
        if shell not in Exp.Tokens_Shell:
            raise error.SyntaxError(token_end)
        if shell in Exp.SHELL_RR and not self.has_subject and len(self) == 1:
            item = self[0]
            # remove shell () if shell is tuple, and the only item is an operator or shells
            if item.head in Exp.Tokens_Operator + Exp.SHELL_RR + [Exp.VARIABLE]:
                last_object = self.pop()
                self.__iadd__(last_object)
                self.head = last_object.head
                self.has_subject = item.has_subject
                self.breakpoint = item.breakpoint
                return
        self.head = shell
        return

    def insert_inner(self, w):
        new_object = TokenTree(self, w)
        self.append(new_object)
        return new_object

    def insert_upper(self, w):
        last_object = self.pop(-1)
        new_object = self.insert_inner(w)
        new_object.append(last_object)
        last_object.parent = new_object
        return new_object

    def insert_root(self, w):
        new_object = TokenTree(None, w)
        new_object.append(self)
        self.parent = new_object
        return new_object

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
        elif self.head in Exp.Tokens_Shell:
            pass
        elif self.head in Exp.IDX:
            if 1 <= len(self) <= 3:
                pass
            else:
                raise error.SyntaxError(self.head)
        elif len(self) != 2:
            raise error.SyntaxError(self.head)
        for token in self:
            if type(token) is TokenTree:
                token.check_sizeof()

    def to_data(self):
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
                    name = '%s%s%s' % (name, Exp.DOT, name_next)
                    i += 1
                else:
                    break
            return Token.from_var(name)
        # is operator
        if self.head in Exp.Tokens_Operator:
            data = [token.to_data() for token in self]
            return Token.from_operator(self.head, *data)
        # if ()
        if self.head in Exp.SHELL_RR:
            data = [token.to_data() for token in self]
            if self.has_subject:
                return Token.from_range(self.head, *data)
            return Token.from_tuple(*data)
        # is range
        if self.head in Exp.Tokens_Shell:
            data = [token.to_data() for token in self]
            return Token.from_range(self.head, *data)

    def __repr__(self):
        has_subject = 'T' if self.has_subject else ''
        return has_subject + self.head + '{ ' + ', '.join([repr(token) for token in self]) + ' }'


class Interpreter:

    def __init__(self, dir_process: str = './', plan=None, monitor=None, header_file=None, *args, **kwargs):
        self.dir_process = os.path.abspath(os.path.join(dir_process))
        plan = Plan if plan is None else plan
        monitor = StdMonitor if monitor is None else monitor
        Exp.EVENT = Event()
        self.plan = plan(self.dir_process, self.code_to_data)
        self.monitor = monitor()
        self._init_builtin_methods(Plan)
        self._init_builtin_methods(self.plan)
        if header_file is not None:
            self.execute_script(header_file)

    @classmethod
    def add_module(cls, module_func):
        Exp.EVENT.add_object(module_func)

    def code_to_data(self, message: str):
        lines = message.split(Exp.NEXTLINE)
        for line in lines:
            tokens = self._scanner(line)
            prefixes, query = self._parser(tokens)
            data = self._semantic_analysis(prefixes, query)
            yield data

    def execute_script(self, path: str):
        path = os.path.join(self.dir_process, path)
        if os.path.exists(path):
            with open(path, 'r') as f:
                self(f.read())

    def begin_interactive(self, debug=False):
        _interactive(self, debug=debug)

    def __call__(self, message: str, lazy_execute: bool = True):
        for data in self.code_to_data(message):
            self.plan.push(data)
            if not lazy_execute:
                self.plan.execute()
        if lazy_execute:
            self.plan.execute()

    def _init_builtin_methods(self, plan):
        external_methods, modules = plan.get_builtin_methods()
        for module_name in external_methods:
            module_func = getattr(modules, module_name)
            self.add_module(module_func)

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
        prefixes = TokenTree(None, Exp.SHELL_RR[0])

        query = TokenTree(None, Exp.VARIABLE)
        object_attr = query
        for w in tokens:
            # comments
            if w == Exp.COMMENT:
                break

            # indents
            if w in Exp.INDENT:
                if object_attr.head == Exp.VARIABLE:
                    # start with character
                    if len(object_attr) > 0:
                        object_attr.append(w)
                elif len(object_attr) > 0:
                    # start with character
                    if type(object_attr[-1]) is str:
                        object_attr.append(w)
                continue

            # exp
            if w in Exp.ADD + Exp.SUB:
                if type(object_attr[-1]) is str:
                    if object_attr[-1].endswith('e') and object_attr[-1][0].isdigit():
                        object_attr.append(w)
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
                # move to shell
                while object_attr.head not in Exp.Tokens_Open:
                    object_attr.tokenize()
                    last_object = object_attr.parent
                    # indices
                    if object_attr.head in Exp.IDX:
                        if last_object is None:
                            raise error.SyntaxError(object_attr.head)
                        object_attr = last_object
                        break
                    # new tuple
                    if last_object is None:
                        # variable -> tuple
                        if object_attr.head == Exp.VARIABLE:
                            object_attr.head = Exp.SHELL_RR[0]
                            break
                        # =
                        if object_attr.head in Exp.IS:
                            if object_attr[-1].head not in Exp.SHELL_RR:
                                object_attr = object_attr.insert_upper(Exp.SHELL_RR[0])
                            else:
                                object_attr = object_attr[-1]
                            break
                        # is tuple
                        object_attr.breakpoint = object_attr.pointer
                        break
                    # else : goto upper
                    object_attr = last_object
                object_attr.tokenize()
                object_attr.breakpoint = object_attr.pointer

            # prefixes
            elif w in Exp.Tokens_Prefix:
                # not from- prefix
                if w not in Exp.FROM:
                    if object_attr.parent is None and object_attr.head == Exp.VARIABLE:
                        if len(query) > 0:
                            prefixes.append(query)
                        prefixes.append(w)
                        prefixes.tokenize()
                        query = TokenTree(None, Exp.SHELL_RR[0])
                        object_attr = query
                        continue
                # from- prefix
                elif object_attr.parent is None and len(object_attr) == 0:
                    prefixes.append(w)
                    prefixes.tokenize()
                    continue
                raise error.SyntaxError(w)

            # open shells
            elif w in Exp.Tokens_Open:
                object_attr.tokenize()
                # in ()
                if object_attr.head in Exp.RBO:
                    # if empty shell : tuple
                    if len(object_attr) == 0:
                        # only ()
                        if w not in Exp.RBO:
                            raise error.SyntaxError(w)
                        object_attr = object_attr.insert_inner(w)
                        object_attr.has_subject = False
                        continue
                    # if comma ahead
                    if len(object_attr) == object_attr.breakpoint:
                        # only ()
                        if w not in Exp.RBO:
                            raise error.SyntaxError(w)
                        object_attr = object_attr.insert_inner(w)
                        object_attr.has_subject = False
                        continue
                    # else : decorate subject
                    object_attr = object_attr.insert_upper(w)
                    object_attr.has_subject = True
                    object_attr.breakpoint = object_attr.pointer
                    continue
                # =
                if object_attr.head in Exp.IS + Exp.DIS:
                    # tuple
                    if len(object_attr) == 1:
                        # only ()
                        if w not in Exp.RBO:
                            raise error.SyntaxError(w)
                        object_attr = object_attr.insert_inner(w)
                        object_attr.has_subject = False
                        continue
                    # decorate object
                    if len(object_attr) == 2:
                        object_attr = object_attr.insert_upper(w)
                        object_attr.has_subject = True
                        object_attr.breakpoint = object_attr.pointer
                        continue
                    raise error.SyntaxError(w)
                # just operators
                if object_attr.head in Exp.Tokens_Operator:
                    # parent is operator
                    if len(object_attr) == 2 and object_attr.head in Exp.Tokens_Operator:
                        object_attr = object_attr.insert_upper(w)
                        object_attr.has_subject = True
                        continue
                    # must be tuple
                    if len(object_attr) != 1:
                        raise error.SyntaxError(w)
                    # only ()
                    if w not in Exp.RBO:
                        raise error.SyntaxError(w)
                    object_attr = object_attr.insert_inner(w)
                    object_attr.has_subject = False
                    continue
                # exception : null query
                if len(query) == 0:
                    # only ()
                    if w not in Exp.RBO:
                        raise error.SyntaxError(w)
                    query = object_attr = object_attr.insert_inner(w)
                    object_attr.has_subject = False
                    continue
                raise error.SyntaxError(w)

            # close shells
            elif w in Exp.Tokens_Close:
                object_attr.tokenize()
                # move to shell pair
                find_shell = False
                while not find_shell:
                    for shell_opens, shell_closes in Exp.Tokens_Shell_Pair.items():
                        if object_attr.head in shell_opens:
                            if w in shell_closes:
                                find_shell = True
                                break
                    # opening not found
                    if not find_shell:
                        object_attr = object_attr.parent
                        if object_attr is None:
                            raise error.SyntaxError(w)
                        object_attr.tokenize()
                # close shell
                object_attr.close(w)
                object_attr = object_attr.parent
                if object_attr is None:
                    raise error.SyntaxError(w)

            # indices
            elif w in Exp.IDX:
                # move to indices shell '('
                while object_attr.head not in Exp.RBO:
                    # not other shells
                    if object_attr.head in Exp.Tokens_Open:
                        raise error.SyntaxError(w)
                    object_attr.tokenize()
                    object_attr = object_attr.parent
                    if object_attr is None:
                        raise error.SyntaxError(w)
                object_attr.tokenize()
                # no begin values
                if len(object_attr) == object_attr.breakpoint:
                    object_attr = object_attr.insert_inner(w)
                    last_object = TokenTree(object_attr, Exp.NUMBER)
                    last_object += [False, Exp.BOOL]
                    object_attr.append(last_object)
                    continue
                # has start values
                if len(object_attr) == object_attr.breakpoint + 1:
                    # has stop values
                    last_object = object_attr[-1]
                    if last_object.head == w:
                        # not stop value defined
                        if len(last_object) == 1:
                            object_attr = object_attr[-1]
                            last_object = TokenTree(object_attr, Exp.NUMBER)
                            last_object += [False, Exp.BOOL]
                            object_attr.append(last_object)
                            continue
                        if len(last_object) == 2:
                            object_attr = last_object
                            continue
                        raise error.SyntaxError(w)
                    # no stop values
                    object_attr = object_attr.insert_upper(w)
                    continue
                raise error.SyntaxError(w)

            # operators
            elif w in Exp.Tokens_Operator:
                # 'n'umber, 'v'ariable, 't'uple
                if w in Exp.ABSTRACT_TYPES:
                    object_attr.append(w)
                    continue
                object_attr.tokenize()
                # unary operators (-)
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
                    object_attr = object_attr.insert_upper(w)
                    continue
                # lower order
                # if in shell
                if object_attr.head in Exp.Tokens_Open:
                    # put operators into shell
                    object_attr = object_attr.insert_upper(w)
                    continue
                last_object = object_attr.parent
                if last_object is None:
                    query = object_attr = object_attr.insert_root(w)
                    continue
                object_attr = last_object.insert_upper(w)
                if object_attr.parent is None:
                    query = object_attr
            # not operators
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
            last_object = object_attr.pop(0)
            object_attr += last_object
            object_attr.head = last_object.head

        # check size of operators
        prefixes.check_sizeof()
        query.check_sizeof()

        # check prefixes
        prefix_from_pair = True
        prefixes_new = TokenTree(None, Exp.SHELL_RR[0])
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
        delete_files = 0
        print_files = 0
        prefixes_iter = iter(prefixes)
        for token in prefixes_iter:
            if type(token[0]) is not str:
                raise error.SyntaxError(token)
            token = token[0]
            # save files
            if token in Exp.FROM:
                prefix_from = next(prefixes_iter)
                prefix_from = Token.from_var(''.join(prefix_from))
            elif token in Exp.SAVE:
                save_files += 1
            # delete files
            elif token in Exp.DELETE:
                delete_files += 1
            # print variables
            elif token in Exp.PRINT:
                print_files += 1
            # check overlap
            if save_files + delete_files + print_files >= 2:
                raise error.SyntaxError(token)

        query = query.to_data()

        # (save, delete, print) files
        for op, test, func in zip([Exp.SAVE[0], Exp.DELETE[0], Exp.PRINT[0]],
                                  [save_files, delete_files, print_files],
                                  [Token.from_save, Token.from_delete, Token.from_print]):
            if not test:
                continue
            if query.data_type == Token.TYPE_VARIABLE:
                return func(prefix_from, query)
            if query.data_type == Token.TYPE_TUPLE:
                return func(prefix_from, *query.args)
            else:
                raise error.SyntaxError(op)
        # just data
        return query
