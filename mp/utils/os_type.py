from platform import system


def _get_os():
    return system().lower()


def is_windows():
    return 'windows' in _get_os()


def is_linux():
    return 'linux' in _get_os()
