from mp import PythonInterpreter
from mp import RemoteInterpreter

from mp.markdown import draw_graph, draw_script

PATH_SCRIPT = 'script'


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


def test_python():
    interpreter = PythonInterpreter(_curdir())
    interpreter('save %s' % PATH_SCRIPT)
    _test(interpreter)

    draw_graph(interpreter.plan.graph)
    draw_script(interpreter.plan.graph)


def test_remote():
    # not totally implemented yet
    pass


if __name__ == '__main__':
    test_python()
    test_remote()
