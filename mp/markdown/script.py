from mp.core.expression import Expression as Exp
from mp.markdown.base import _BaseWriter


class ScriptWriter(_BaseWriter):
    """
        The following code relies on the 'markdown' script.
    """

    def __init__(self, filename: str = None, level: int = _BaseWriter.LEVEL[-1]):
        super().__init__(filename, level, 'mp')

        self.vars = list()

    def _draw_var(self, var):
        if var is None:
            return
        if var.symbol in self.vars:
            return

        if var.is_variable:
            if var.toward is not None:
                # not parameter
                if not self.describe(detail=True) and var.symbol.startswith('_'):
                    return
                # not pre-defined variable
                if not self.describe(detail=True) and var.symbol in ['true', 'false', 'none']:
                    return
                # else
                if not var.toward.is_placeholder:
                    self(self._encode(var))
        if var.is_method_delegate and not var.is_method_defined and not var.is_builtins:
            if self.describe(detail=True):
                self(self._encode(var))

    def _draw_vars(self, args):
        for arg in args:
            self._draw_var(arg)

    def _encode(self, var):
        if (var.is_variable or var.is_method_delegate) and not var.is_method_defined:
            if var.symbol in self.vars:
                return var.symbol
            self.vars.append(var.symbol)

        if var.is_variable:
            if var.toward is None:
                return var.name
            if var.toward.is_placeholder:
                return var.name
            op = ':=' if var.is_pointer_orient else '='
            self._draw_var(var.toward)
            return '%s %s %s' % (var.name, op, self._encode(var.toward))
        if var.is_constant:
            return '%s' % var.encode()
        if var.is_operator:
            if var.op in Exp.IDX:
                return self._index(var)
            if var.op in Exp.Tokens_Operator:
                self._draw_vars([var.sub, var.obj])
                sub = self._wrap(var.op, var.sub)
                obj = self._wrap(var.op, var.obj)
                op = var.op
                if op in Exp.Tokens_In2Out.keys():
                    op = Exp.Tokens_In2Out[op]
                return '%s %s %s' % (sub, op, obj)
        if var.is_indices:
            return self._shell(var, '(', ')')
        if var.is_transpose:
            return self._shell(var, '{', '}')
        if var.is_view:
            return self._shell(var, '[', ']')
        if var.is_method_defined:
            sub = var.name
            self._draw_vars(var.args + [var.toward])
            args = [self._encode(arg) for arg in var.args]
            args += [self._encode(var.toward)]
            return '%s(%s)' % (sub, ', '.join(args))
        if var.is_method_delegate:
            sub = var.name
            self._draw_var(var.toward)
            if var.is_builtins:
                return sub
            toward = self._wrap('()', var.toward)
            if var.repeat is not None:
                self._draw_var(var.repeat)
                toward = '%s * %s' % (toward, self._wrap('*', var.repeat))
            return '%s = %s' % (sub, toward)
        if var.is_method:
            sub = var.name
            if var.toward is not None:
                self._draw_var(var.toward)
            if var.repeat is not None:
                self._draw_var(var.repeat)
                sub = '(%s * %s)' % (sub, self._wrap('*', var.repeat))
            self._draw_vars(var.args)
            args = [self._encode(arg) for arg in var.args]
            return '%s(%s)' % (sub, ', '.join(args))
        if var.is_tuple:
            args = [self._encode(arg) for arg in var.args]
            return '(%s)' % ', '.join(args)

    def _shell(self, var, c_open, c_close):
        sub = ''
        if var.sub is not None:
            self._draw_var(var.sub)
            sub = self._wrap(var.op, var.sub)
        self._draw_vars(var.args)
        args = [self._encode(arg) for arg in var.args]
        return '%s%s%s%s' % (sub, c_open, ', '.join(args), c_close)

    def _index(self, var):
        def _index_encode(target, str_format, default):
            if target is not None:
                default = str_format % self._wrap(var.op, target)
            return default

        self._draw_vars([var.sub, var.obj, var.step])
        sub = _index_encode(var.sub, '%s:', ':')
        obj = _index_encode(var.obj, '%s', '')
        step = _index_encode(var.step, ':%s', '')
        return '%s%s%s' % (sub, obj, step)

    def _wrap(self, var_op, target):
        code = self._encode(target)
        if target.is_operator:
            if Exp.Tokens_Order[var_op] > Exp.Tokens_Order[target.op]:
                return '(%s)' % code
        return code

    def _comment(self, msg):
        self('# %s' % msg)

    def flush(self):
        super().flush()
        self._comment('Auto-Generated from Mp-ScriptWriter')
        self._comment('-----------------------------------')
        self()


draw_script = ScriptWriter.draw
