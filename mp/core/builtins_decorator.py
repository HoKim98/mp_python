from mp.core.event import EventUnit

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

    # For custom dataset
    @classmethod
    def dataset(cls, header: str, candidates):
        method = cls.header(header, fixed=True, hidden=True)
        method.add_attr('base_dir', header)
        method.add_attr('candidates', candidates)
        return method

    # For binary operator
    # scope = globals()
    @classmethod
    def binary(cls, name: str, op, scope):
        def wrapper(x, y, _=None):
            return op(x, y)
        method = cls.static(name)(wrapper)
        scope['method_%s' % name[2:]] = method


class _ExtensionWrapper:
    def __init__(self, regex: str, fixed: bool, hidden: bool):
        self._unit = EventUnit(regex, None, True, fixed, hidden, is_regex=True)
        self._attr = dict()

    def add_attr(self, key, value):
        self._attr[key] = value

    def __call__(self, method):
        self._unit.set_method(method)
        for key, value in self._attr.items():
            setattr(self._unit, key, value)
        return self._unit
