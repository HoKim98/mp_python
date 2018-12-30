from mp.core.expression import Expression as Exp
from mp.markdown.base import _BaseWriter


class GraphWriter(_BaseWriter):
    """
        The following code relies on the 'mermaid' library.
        https://mermaidjs.github.io/
    """

    NODE_IDX = ['|sub|', '|obj|', '|step|', '|repeat|']
    VIEWPOINTS = ['LR', 'TD', ]

    SPECIAL_CHAR = {
        '-': ' - ',
    }

    def __init__(self, filename: str = None, viewpoint: str = VIEWPOINTS[0], level: int = _BaseWriter.LEVEL[-1]):
        self.viewpoint = 'graph %s' % viewpoint
        self.level = level
        super().__init__(filename, level, 'mg')

        self.vars = list()
        self.ops = list()

    def _draw_var(self, var):
        if var in self.vars:
            return
        self.vars.append(var)

        if var.is_variable:
            if var.toward is not None:
                self._draw_var(var.toward)
                self(self._node(var.toward, var))
            else:
                self(self._edge(var))
        elif var.is_constant:
            pass
        elif var.is_tuple:
            args = [None] * 4 + list(var.args)
            for idx, arg in enumerate(args):
                if arg is not None:
                    self._draw_var(arg)
                    self(self._node(arg, var, idx))
        elif var.is_operator or var.is_method:
            args = [var.sub, var.obj, var.step, var.repeat] + list(var.args)
            for idx, arg in enumerate(args):
                if arg is not None:
                    self._draw_var(arg)
                    self(self._node(arg, var, idx))
        else:
            raise NotImplementedError

    def _node(self, node_from, node_to, node_idx: int = -1):
        node_from = self._edge(node_from)
        node_to = self._edge(node_to)
        node_idx = self._idx(node_idx)
        msg = '%s -->%s %s' % (node_from, node_idx, node_to)
        return msg

    def _edge(self, edge):
        code = self._encode(edge)
        symbol = edge.symbol
        if symbol in Exp.Tokens_In2Out.keys():
            symbol = Exp.Tokens_In2Out[symbol]
        if symbol in self.SPECIAL_CHAR.keys():
            symbol = self.SPECIAL_CHAR[symbol]
        if edge.is_constant:
            return '%s(%s)' % (code, symbol)
        if edge.is_variable:
            return '%s[%s]' % (code, symbol)
        if edge.is_operator:
            return '%s(%s)' % (code, symbol)
        if edge.is_method:
            return '%s{%s}' % (code, symbol)
        raise NotImplementedError

    def _idx(self, node_idx):
        if node_idx < 0:
            return ''
        arg_start = len(self.NODE_IDX)
        if node_idx < arg_start:
            return self.NODE_IDX[node_idx]
        return '|arg #%d|' % (node_idx - arg_start)

    def _encode(self, edge):
        if edge.is_variable:
            return edge.symbol
        if edge.is_constant:
            return edge.symbol
        if edge.is_operator or edge.is_method or edge.is_method_defined:
            if edge in self.ops:
                idx = self.ops.index(edge)
            else:
                self.ops.append(edge)
                idx = len(self.ops) - 1
            return '?%s' % idx
        raise NotImplementedError

    def flush(self):
        super().flush()
        self(self.viewpoint)
        self()


draw_graph = GraphWriter.draw
