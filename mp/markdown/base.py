from mp.core.expression import Expression as Exp
from mp.utils import assert_filename


class _BaseWriter:
    """
        The following code relies on the 'markdown' script.
    """

    LEVEL = [1, 2, 3, ]
    USE_TOGGLE_NAME = True

    def __init__(self, filename: str, level: int, extension: str):
        self.filename = assert_filename(filename, extension)
        self.level = level
        self.buffer = ''
        self.flush()

    def _draw_var(self, var):
        raise NotImplementedError

    def __call__(self, msg: str = ''):
        if msg is None:
            return
        self.buffer += '%s\n' % msg

    def save(self, flush=True):
        if self.filename is not None:
            with open(self.filename, 'w') as f:
                f.write(self.buffer)
        if flush:
            self.flush()

    def flush(self):
        self.buffer = ''

    @classmethod
    def _graph_to_vars(cls, graph):
        return graph.vars.values()

    class _toggle_method_name:
        def __init__(self, graph_vars, toggle_name):
            self.graph_vars = graph_vars
            self.toggle_name = toggle_name

        def __enter__(self):
            if not self.toggle_name:
                return
            for var in self.graph_vars:
                var.name_bak = var.name
                if var.is_method and var.name.startswith(Exp.CODE_CONST):
                    var.name = var.get_real_method()

        def __exit__(self, *args, **kwargs):
            if not self.toggle_name:
                return
            for var in self.graph_vars:
                var.name = var.name_bak
                delattr(var, 'name_bak')

    def describe(self, rough: bool = False, normal: bool = False, detail: bool = False):
        result = False
        if rough:
            result = result or self.level == 1
        if normal:
            result = result or self.level == 2
        if detail:
            result = result or self.level == 3
        return result

    @classmethod
    def draw(cls, graph, filename: str = None, level: int = LEVEL[-1], *args, **kwargs):
        writer = cls(filename, level, *args, **kwargs)
        graph_vars = cls._graph_to_vars(graph)
        with cls._toggle_method_name(graph_vars, cls.USE_TOGGLE_NAME):
            for var in graph_vars:
                writer._draw_var(var)
        writer.save(flush=False)
        return writer.buffer
