import re

__all__ = ['extension', ]


class extension:
    def __new__(cls, regex: str):
        return _ExtensionWrapper(regex)

    @classmethod
    def static(cls, var_name: str):
        regex = r'^%s$' % var_name
        return _ExtensionWrapper(regex)


class _ExtensionWrapper:
    def __init__(self, regex: str):
        self._method_name = regex
        self._method_name_compiled = re.compile(self.method_name)
        self._method = None

    @property
    def method_name(self):
        return self._method_name

    def test(self, var_name: str):
        return self._method_name_compiled.search(var_name) is not None

    def execute(self, toward, args):
        return self._method(toward, args)

    def __call__(self, method):
        self._method = method
        return self

    def __repr__(self):
        return '[Extension] %s' % self.method_name
