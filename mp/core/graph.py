from collections import OrderedDict

from mp.core.data import *
from mp.core.error import RequiredError, SyntaxError
from mp.core.expression import Expression as Exp


class Graph:

    def __init__(self):
        super().__init__()
        # count 1 if self.alloc
        self.window = 0
        # variables
        self.vars = dict()
        # save/delete files sometime
        self.ios = OrderedDict()
        # print files sometime
        self.prints = OrderedDict()
        # point self
        self.var_self = list()

    # make new variable name
    def new_name(self):
        name = '%s%s' % (Exp.CODE_CONST, self.window)
        self.window += 1
        return name

    # allocate new constant
    def alloc(self, num_type, toward, name=None):
        if name is None:
            name = self.new_name()
        var = Constant(name, num_type, toward)
        self.vars[name] = var
        return var

    # allocate new variable by force
    def alloc_f(self, name, toward):
        if name in self.vars.keys():
            self.gc(self.vars[name])
        var = Variable(name, toward)
        self.vars[name] = var
        return var

    # allocate new pointer variable
    def alloc_p(self, toward=None):
        name = self.new_name()
        return self.alloc_f(name, toward)

    # get or allocate variable
    def find(self, name):
        # name is not defined
        if name in Exp.REQUIRED:
            return Required()
        # this is a method
        method = Exp.EVENT.find_unique(name)
        if method is not None:
            return Builtins(name)
        # this is user-defined method
        if name in Exp.METHOD:
            return UserDefinedMethod(name)
        # replace 'self'
        if name.startswith(Exp.CODE_SELF):
            name = '%s%s' % (self.get_self(), name[len(Exp.CODE_SELF):])
        # find in graph
        if name in self.vars.keys():
            return self.vars[name]
        # find in file sometime
        var = Variable(name)
        self.vars[name] = var
        return var

    # rename a variable
    def rename(self, name_from, name_to):
        # not exists
        if name_from not in self.vars.keys():
            return
        old = self.vars[name_from]
        # useless
        if old.is_required:
            self.gc(old)
            return
        old.name = name_to
        self.vars[name_to] = old
        del self.vars[name_from]

    # point existing method
    def point_method(self, name, toward, repeat=None):
        # no user-defined method pointer
        if toward.is_method_defined:
            # if just declaring
            if toward.toward is None:
                raise RequiredError(toward.name)
        self.rename(name, self.new_name())
        sub = Method(name, toward, repeat=repeat)
        sub.name = name
        self.vars[name] = sub
        return sub

    # save sometime
    def save(self, dir_from, *args, save=True, filesystem=True):
        if dir_from is not None:
            if type(dir_from) is not Variable:
                raise SyntaxError(dir_from.symbol)
            dir_from = dir_from.symbol
        for file in args:
            if type(file) not in (Variable, Method):
                raise SyntaxError(file.symbol)
            # copy data
            if dir_from is not None:
                name = '%s%s%s' % (dir_from, Exp.DOT, file.name)
                self.rename(file.name, name)
            else:
                name = file.name
            # remove vars
            if not save:
                old = file.toward
                file.toward = None
                self.gc(file)
                self.gc(old)
            # (save, delete) or (print) files
            wait_list = self.ios if filesystem else self.prints
            wait_list[name] = save

    # delete sometime
    def delete(self, dir_from, *args):
        self.save(dir_from, *args, save=False)

    # print sometime
    def print(self, dir_from, *args):
        self.save(dir_from, *args, filesystem=False)

    # choose whether remove
    def gc(self, var):
        if var is None:
            return True
        name = var.name
        if name is None:
            return True
        # is constant
        if var.is_constant:
            if name in self.vars.keys():
                del self.vars[name]
            del var
            return True
        # is operator
        if var.is_operator:
            items = [var.sub, var.obj, var.step]
            items += var.args
            # test removing
            is_removed = False
            for item in items:
                is_removed = self.gc(item) or is_removed
            if is_removed:
                del var
            return is_removed
        # is user-defined method
        if var.is_method_defined:
            self.gc(var.repeat)
            self.gc(var.toward)
            for arg in var.args:
                self.gc(arg)
            del var
            return True
        # is variable
        if var.is_variable or var.is_method_delegate:
            # already removed
            if name not in self.vars.keys() and var.is_variable:
                return True
            # is actually constant
            if name.startswith('/'):
                old = var.toward
                var.toward = None
                self.gc(old)
                del self.vars[name]
                del var
                return True
            # else
            if var.toward is None:
                # find using
                use_item = False
                for var_name, item in self.vars.items():
                    if var_name == name:
                        continue
                    if item.has_attr(name):
                        use_item = True
                        break
                # useless
                if not use_item:
                    # remove delegate
                    old = var.repeat
                    var.repeat = None
                    self.gc(old)
                    for arg in var.args:
                        self.gc(arg)
                    # with variable
                    if name in self.vars.keys():
                        del self.vars[name]
                    del var
                    return True
            return False
        # if method
        if var.is_method:
            self.gc(var.repeat)
            self.gc(var.toward)
            for arg in var.args:
                self.gc(arg)
            for arg in var.kwargs.values():
                self.gc(arg)
            # never enter toward
            if var.toward is not None:
                return False
            del var
            return True
        # else
        # find using
        if name in self.vars.keys():
            use_item = False
            for var_name, item in self.vars.items():
                if var_name == name:
                    continue
                if item.has_attr(name):
                    use_item = True
                    break
            # useless
            if not use_item:
                # remove args if method
                for arg in var.args:
                    self.gc(arg)
                for arg in var.kwargs.values():
                    self.gc(arg)
                del self.vars[name]
                self.gc(var.toward)
                self.gc(var.repeat)
                del var
                return True
        # else
        del var
        return True

    # detach from graph
    def detach(self, name):
        if name in self.vars.keys():
            self.vars[name] = self.vars[name].copy()

    # for in-place operators
    def inplace(self, sub, obj):
        # only variable, method, tuple in sub
        name = sub.name
        if not (sub.is_variable or sub.is_method or sub.is_operator):
            raise SyntaxError(name)
        # point method
        if obj.is_method_delegate:
            # no tuple-delegate
            if sub.is_tuple:
                raise SyntaxError(Exp.IS[0])
            # else
            self.point_method(name, obj)
            return self.vars[name]
        # var-tuple
        if not sub.is_tuple and obj.is_tuple:
            # only var-tuple
            if not sub.is_variable:
                raise SyntaxError(Exp.IS[0])
            # substitute
            old = sub.toward
            sub.toward = obj
            self.gc(old)
            return sub
        # tuple-var
        if sub.is_tuple and not obj.is_tuple:
            # only tuple-var(tuple)
            if obj.is_variable:
                if obj.toward.is_tuple:
                    return self.inplace(sub, obj.toward)
                else:
                    raise SyntaxError(Exp.IS[0])
            else:
                raise SyntaxError(Exp.IS[0])
        # tuple-tuple
        if sub.is_tuple and obj.is_tuple:
            # only same dims
            if len(sub.args) != len(obj.args):
                raise SyntaxError(Exp.IS[0])
            # in-place in order
            for arg_sub, arg_obj in zip(sub.args, obj.args):
                self.inplace(arg_sub, arg_obj)
            return sub
        # else (tuple-var, var-var)
        # rename if recursion
        if sub.is_variable:
            if obj.has_attr(name):
                # check target is pointer
                old = self.vars[name]
                if old.is_required:
                    raise RequiredError(name)
                # else
                # replace sub with sub.toward
                obj = obj.replace(name)
                sub.toward = obj
                return sub
        # substitute
        # remove previous
        old = sub.toward
        sub.toward = obj
        self.gc(old)
        return sub

    # for normal operators
    def operate(self, op, sub, obj=None, step=None):
        # remove delegate
        if sub.is_method_delegate:
            if sub.name in self.vars.keys():
                del self.vars[sub.name]
            toward = sub.toward
            sub.toward = None
            self.gc(toward)
            self.gc(sub)
            sub = self.find(sub.name)
        # =
        if op in Exp.IS:
            return self.inplace(sub, obj)
        # := (disposable substitute)
        if op in Exp.DIS:
            sub.is_pointer = True
            sub.is_pointer_orient = True
            # can substitute
            if sub.toward is None:
                name = sub.name
                if obj.has_attr(name):
                    raise RequiredError(sub.symbol)
                sub.toward = obj
                return sub
            # else
            # remove obj
            self.gc(obj)
            return sub
        # in-place operators
        if op in Exp.Tokens_Inplace:
            if sub.toward is None:
                raise RequiredError(sub.name)
            tmp = Operator(op, sub.toward, obj, step)
            return self.inplace(sub, tmp)
        # out-place operators
        tmp = Operator(op, sub, obj, step)
        return tmp

    # cleanup io requests
    def clear(self):
        self.ios = OrderedDict()
        self.prints = OrderedDict()

    # (:, :, ...)
    @classmethod
    def indices(cls, *args):
        return Indexed(*args)

    # {}
    @classmethod
    def transpose(cls, *args):
        return Transpose(*args)

    # []
    @classmethod
    def view(cls, *args):
        return View(*args)

    # tuple
    @classmethod
    def tuple(cls, *args):
        return Tuple(*args)

    # :
    @classmethod
    def slice(cls, start, stop, step):
        op = Exp.IDX[0]
        return Operator(op, start, stop, step)

    @classmethod
    def set_placeholder(cls, var):
        var.toward = Placeholder()

    def get_self(self):
        for name in reversed(self.var_self):
            if name is not None:
                return '%s%s' % (self.var_self[-1], Exp.DOT)
        return ''

    def push_self(self, name: str = None):
        self.var_self.append(name)

    def pop_self(self):
        self.var_self.pop(-1)
