import re as _re

from mp.core.expression import Expression as Exp


class EventUnit:
    def __init__(self, event_name: str, method, unique, fixed, hidden, is_regex: bool = False):
        self._event_name = event_name
        self._event_name_compiled = _re.compile(self._event_name) if is_regex else None
        self._method = method
        self._unique = unique
        self._fixed = fixed
        self._hidden = hidden

    def match_name(self, name: str, hidden: bool = False):
        if self._hidden and not hidden:
            return False
        if self._event_name_compiled is not None:
            return self._event_name_compiled.search(name) is not None
        return self._event_name == name

    def get_method(self):
        return self._method

    def set_method(self, method):
        self._method = method

    def __call__(self, *args, **kwargs):
        return self._method(*args, **kwargs)

    @property
    def fixed(self) -> bool:
        return self._fixed

    @property
    def hidden(self) -> bool:
        return self._hidden

    @property
    def unique(self) -> bool:
        return self._unique

    @property
    def name(self) -> str:
        return self._event_name

    def __str__(self):
        return self.name


class EventDelegate:
    def __init__(self, event_name: str, hidden: bool):
        self._event_name = event_name
        self._hidden = hidden

    def __call__(self, *args, **kwargs):
        kwargs['hidden'] = self._hidden
        return Exp.EVENT(self._event_name, *args, **kwargs)


class Event:
    def __init__(self, verbose: bool = False):
        self._events = list()
        self._uniques = dict()
        self._verbose = verbose

    def add(self, event_name: str, method, unique: bool = False,
            fixed: bool = False, hidden: bool = False, is_regex: bool = False):
        event = EventUnit(event_name, method, unique, fixed, hidden, is_regex)
        if unique:
            self.remove(event_name)
            self._uniques[event_name] = event
        self._events.append(event)

    def add_object(self, unit: EventUnit):
        assert type(unit) is EventUnit
        if unit._unique:
            self.remove(unit._event_name)
            self._uniques[unit._event_name] = unit
        self._events.append(unit)

    def find(self, event_name: str, hidden: bool = False, get_idx: bool = False, _no_re: bool = False):
        def _compare():
            if _no_re:
                return event._event_name == event_name
            return event.match_name(event_name, hidden)

        for idx, event in enumerate(self._events):
            if _compare():
                if get_idx:
                    return idx, event
                return event
        if get_idx:
            return -1, None
        return None

    def find_unique(self, event_name: str, hidden: bool = False):
        for event in self._uniques.values():
            if event.match_name(event_name, hidden):
                return event
        return None

    def remove(self, event_name: str):
        idx, event = self.find(event_name, hidden=True, get_idx=True, _no_re=True)
        if event_name in self._uniques.keys():
            del self._uniques[event_name]
        if idx >= 0:
            del self._events[idx]

    def __call__(self, event_name: str, *args, hidden: bool = False, **kwargs):
        list_responses = list()
        for event in self._events:
            if event.match_name(event_name, hidden):
                response = event(*args, **kwargs)
                self._add_response(list_responses, response)
                if response is not None and event.unique:
                    return list_responses[-1]
        return list_responses

    @classmethod
    def delegate(cls, event_name: str, hidden: bool = False):
        return EventDelegate(event_name, hidden)

    @classmethod
    def _add_response(cls, list_responses, response):
        if response is not None:
            list_responses.append(response)
