__all__ = ['__version__', 'PythonInterpreter', 'RemoteInterpreter']
from mp.version import __doc__, __version__
try:
    from mp.engine import PythonInterpreter, RemoteInterpreter

except ImportError as e:
    print('[Mp Import Error] ' + str(e))
