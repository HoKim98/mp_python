class EventUnit:
    def __init__(self, event_name: str, method):
        self._event_name = event_name
        self._method = method

    def match_name(self, match_name: str):
        return self._event_name == match_name

    def get_method(self):
        return self._method

    def __call__(self, event_name: str, *args, **kwargs):
        if self._event_name == event_name:
            return self._method(*args, **kwargs)
        return None


class Event:
    def __init__(self):
        self.events = list()

    def add(self, event_name: str, method):
        event = EventUnit(event_name, method)
        self.events.append(event)

    def __call__(self, event_name: str, *args, **kwargs):
        list_responses = list()
        for event in self.events:
            response = event(event_name, *args, **kwargs)
            self._add_response(list_responses, response)
        return list_responses

    @classmethod
    def _add_response(cls, list_responses, response):
        if response is not None:
            list_responses.append(response)
