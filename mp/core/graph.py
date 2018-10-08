from mp.core.data import Builtins, Constant, Indexed, Operator, Required, Variable, View
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
        self.ios = dict()
        # do not make pointer
        self.lock_point = False

    # make new variable name
    def new_name(self):
        name = '/%s' % self.window
        self.window += 1
        return name

    # allocate new constant
    def alloc(self, num_type, toward, name=None):
        if name is None:
            name = '/%s' % self.window
            self.window += 1
        var = Constant(name, num_type, toward)
        self.vars[name] = var
        return var

    # allocate new variable by force
    def alloc_f(self, name, toward):
        var = Variable(name, toward)
        self.vars[name] = var
        return var

    # allocate new pointer variable
    def alloc_p(self, toward=None):
        name = self.new_name()
        return self.alloc_f(name, toward)

    # get or allocate variable
    def find(self, name):
        if name in Exp.REQUIRED:
            return Required()
        if name in Exp.BUILTINS:
            return Builtins(name)

        if name in self.vars.keys():
            return self.vars[name]
        # find in file sometime
        var = Variable(name)
        self.vars[name] = var
        return var

    # rename a variable
    def rename(self, name_from, name_to):
        old = self.vars[name_from]
        # if old is required
        if old.toward is None:
            raise RequiredError(name_from)
        old.name = name_to
        self.vars[name_to] = old
        del self.vars[name_from]

    # call function or get indices
    def call(self, name, *args):
        sub = self.find(name)
        if sub.is_variable:
            return Indexed(sub, *args)
        if sub.is_method:
            sub.sub = name
            sub.args = args
            return sub
        raise SyntaxError(name)

    # (:, :, ...)
    def indices(self, *args):
        return Indexed(*args)

    # {}
    def view(self, *args):
        return View(*args)

    # :
    def slice(self, sub, obj=None):
        op = Exp.IDX[0]
        if sub.is_operator:
            if sub.op in Exp.IDX:
                if sub.step is None:
                    sub.step = obj
                    return sub
                raise SyntaxError(op)
        return Operator(op, sub, obj)

    # save sometime
    def save(self, dir_from, *args, save=True):
        if dir_from is not None:
            if type(dir_from) is not Variable:
                raise SyntaxError(dir_from.symbol)
            dir_from = dir_from.symbol
        for file in args:
            if type(file) is not Variable:
                raise SyntaxError(file.symbol)
            # copy data
            if dir_from is not None:
                name = '%s.%s' % (dir_from, file.name)
                self._inplace(self.find(name), file)
            else:
                name = file.name
            self.ios[name] = save
            # self.ios[name] = file.toward is not None

    # delete sometime
    def delete(self, dir_from, *args):
        for file in args:
            file.toward = None
        self.save(dir_from, *args, save=False)

    # for in-place operators
    def _inplace(self, sub, obj):
        if obj.has_attr(sub.name):
            name = sub.name
            self.rename(name, self.new_name())
            sub = self.alloc_f(name, obj)
            return sub
        sub.toward = obj
        return sub

    # for normal operators
    def operate(self, op, sub, obj=None, step=None):
        if op in Exp.IS:
            return self._inplace(sub, obj)
        if op in Exp.OIS:
            if self.lock_point:
                return self._inplace(sub, obj)
            if sub.toward is None:
                name = sub.name
                if obj.has_attr(name):
                    raise RequiredError(name)
                sub.toward = obj
                sub.is_pointer = True
                sub.is_pointer_orient = True
                return sub
                #return self.operate(Exp.IS[0], sub, obj, step)
            return sub
        if op in Exp.Tokens_Inplace:
            tmp = self.alloc_p(sub.toward)
            tmp = Operator(op, tmp, obj, step)
            return self._inplace(sub, tmp)
        tmp = self.alloc_p(sub)
        tmp = Operator(op, tmp, obj, step)
        return tmp

    # cleanup io requests
    def clean(self):
        self.ios = dict()
