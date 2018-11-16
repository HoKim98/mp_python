import sys
from platform import system


def _get_os():
    return system().lower()


def is_windows():
    return 'windows' in _get_os()


def is_linux():
    return 'linux' in _get_os()


def get_python_version():
    return '%s.%s' % (sys.version_info.major, sys.version_info.minor)


def get_os():
    return _get_os()
