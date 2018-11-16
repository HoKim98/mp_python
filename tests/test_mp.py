from mp import PythonInterpreter
from mp import PyTorchInterpreter
from mp import RemoteInterpreter

from mp.markdown import draw_graph, draw_script
from mp.dataset import core

PATH_SCRIPT = 'script'
core.FIXED_TTY_WIDTH = True


def _curdir():
    import os
    return os.path.abspath(os.path.join(__file__, os.path.pardir))


def _test(interpreter):
    code = 'a'.encode()[0]
    attrs = interpreter.plan.attr
    while True:
        name = '%st' % bytes([code]).decode()
        if name not in attrs.dict.keys():
            break
        assert attrs[name].get_value()
        code += 1


def _test_specific_interpreter(interpreter):
    interpreter('save %s' % PATH_SCRIPT)
    _test(interpreter)

    draw_graph(interpreter.plan.graph)
    draw_script(interpreter.plan.graph)


def _test_specific_interpreter_run_mnist(interpreter):
    interpreter.execute_script('script_mnist.mp')

    draw_graph(interpreter.plan.graph)
    draw_script(interpreter.plan.graph)


def test_python():
    interpreter = PythonInterpreter(_curdir())
    _test_specific_interpreter(interpreter)


def test_pytorch():
    interpreter = PyTorchInterpreter(_curdir())
    _test_specific_interpreter(interpreter)
    _test_specific_interpreter_run_mnist(interpreter)


def test_remote():
    interpreter = RemoteInterpreter(_curdir())
    pass


if __name__ == '__main__':
    test_python()
    test_pytorch()
    test_remote()
