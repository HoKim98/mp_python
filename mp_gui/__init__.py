__all__ = ['__version__', 'MpGui']
from mp_gui.version import __doc__, __version__
try:
    from mp_gui.layout import MpGui

except ImportError as e:
    print('[MpGui Import Error] ' + str(e))
