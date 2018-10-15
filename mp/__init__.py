__all__ = ['__version__', 'PythonInterpreter']
from mp.version import __doc__, __version__
try:
    from mp.engine import PythonInterpreter

except ImportError as e:
    print('[Mp Import Error] ' + str(e))
