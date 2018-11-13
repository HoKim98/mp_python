from mp.core.io import IO as _IO
from mp.engine.python import attribute as _attr


class IO(_IO):

    @classmethod
    def _load_binary_raw(cls, path):
        return _attr.np.load(path)

    @classmethod
    def _save_binary(cls, path: str, value):
        _attr.np.save(path, value, allow_pickle=False)
