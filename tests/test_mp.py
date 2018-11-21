from mp import PythonInterpreter
from mp import PyTorchInterpreter
from mp import RemoteInterpreter

from mp.markdown import draw_graph, draw_script
from mp.dataset import core

SCRIPT = 'save script'
SCRIPT_METHOD = 'save script_method'
SCRIPT_MNIST = 'save script_mnist'

# --------------------------------------------------------------------------
#             METHOD
# --------------------------------------------------------------------------


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


def _test_markdown(interpreter):
    draw_graph(interpreter.plan.graph)
    draw_script(interpreter.plan.graph)


def _test_specific_interpreter(interpreter, script):
    interpreter(script)
    _test(interpreter)
    _test_markdown(interpreter)

# --------------------------------------------------------------------------
#             TEST
# --------------------------------------------------------------------------


def test_python():
    interpreter = PythonInterpreter(_curdir())
    _test_specific_interpreter(interpreter, SCRIPT)


def test_pytorch():
    interpreter = PyTorchInterpreter(_curdir())
    _test_specific_interpreter(interpreter, SCRIPT)


def test_pytorch_method():
    interpreter = PyTorchInterpreter(_curdir())
    _test_specific_interpreter(interpreter, SCRIPT_METHOD)


def test_pytorch_mnist():
    interpreter = PyTorchInterpreter(_curdir())
    interpreter(SCRIPT_MNIST)
    _test_markdown(interpreter)


def test_remote():
    interpreter = RemoteInterpreter(_curdir())
    pass
