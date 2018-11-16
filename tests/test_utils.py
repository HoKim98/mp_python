def test_utils_console():
    from mp import PythonInterpreter
    i = PythonInterpreter()
    try:
        i.begin_interactive()
    except IOError:
        pass


def test_utils_dependency():
    from mp.utils import dependency
    dependency.get_pytorch()


def test_utils_filename():
    from mp.utils import filename
    filename.assert_filename(None, 'mp')
    filename.assert_filename('a', 'mp')
    filename.assert_filename('a.mp', 'mp')


def test_utils_environment():
    from mp.utils import environment
    environment.get_python_version()
    environment.get_os()
    environment.is_linux()
    environment.is_windows()
    environment.system()


def test_utils_find_interpreter():
    from mp.core.error import NotInCandidate
    from mp.utils import find_interpreter
    find_interpreter('Python')
    find_interpreter('PyTorch')
    try:
        find_interpreter('Potato', error_exit=False)
    except NotInCandidate:
        pass
