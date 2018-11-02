from mp.core.expression import Expression as Exp
from mp.utils import assert_filename


class _BaseWriter:
    """
        The following code relies on the 'markdown' script.
    """

    def __init__(self, filename: str, extension: str):
        self.filename = assert_filename(filename, extension)
        self.buffer = ''
        self.flush()

    def _draw_var(self, var):
        raise NotImplementedError

    def __call__(self, msg: str = ''):
        self.buffer += '%s\n' % msg

    def save(self, flush=True):
        if self.filename is not None:
            with open(self.filename, 'w') as f:
                f.write(self.buffer)
        if flush:
            self.flush()

    def flush(self):
        self.buffer = ''

    class _toggle_method_name:
        def __init__(self, graph_vars):
            self.graph_vars = graph_vars

        def __enter__(self):
            for var in self.graph_vars:
                var.name_bak = var.name
                if var.is_method and var.name.startswith(Exp.CODE_CONST):
                    var.name = var.get_real_method()

        def __exit__(self, *args, **kwargs):
            for var in self.graph_vars:
                var.name = var.name_bak
                delattr(var, 'name_bak')

    @classmethod
    def draw(cls, graph, filename: str = None, *args, **kwargs):
        writer = cls(filename, *args, **kwargs)
        with cls._toggle_method_name(graph.vars.values()):
            for var in graph.vars.values():
                writer._draw_var(var)
        writer.save(flush=False)
        return writer.buffer
