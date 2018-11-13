import re

__all__ = ['extension', ]


class extension:
    def __new__(cls, regex: str, fixed: bool = False, hidden: bool = False):
        return _ExtensionWrapper(regex, fixed, hidden)

    # In case of not using regular expressions
    @classmethod
    def static(cls, var_name: str, fixed: bool = False, hidden: bool = False):
        var_name = var_name.replace(' ', '')
        regex = r'^%s$' % var_name
        return _ExtensionWrapper(regex, fixed, hidden)

    @classmethod
    def header(cls, header: str, fixed: bool = False, hidden: bool = False):
        var_name = header.replace(' ', '')
        regex = r'^%s[.].*' % var_name
        return _ExtensionWrapper(regex, fixed, hidden)


class _ExtensionWrapper:
    def __init__(self, regex: str, fixed: bool, hidden: bool):
        self._method_name = regex
        self._method_name_compiled = re.compile(self.method_name)
        self._method = None
        self._fixed = fixed
        self._hidden = hidden

    @property
    def method_name(self):
        return self._method_name

    @property
    def fixed(self) -> bool:
        return self._fixed

    @property
    def hidden(self) -> bool:
        return self._hidden

    def test(self, var_name: str, find_hidden: bool = False):
        return self._method_name_compiled.search(var_name) is not None and (not self.hidden or find_hidden)

    def execute(self, toward, args, plan):
        return self._method(toward, args, plan)

    def __call__(self, method):
        self._method = method
        return self

    def __repr__(self):
        return '[Extension] %s' % self.method_name
