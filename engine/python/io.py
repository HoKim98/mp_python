from core.io import IO as _IO
from engine.python import attribute as _attr


class IO(_IO):

    @classmethod
    def _load_binary_raw(cls, path):
        raw = _attr.np.load(path)
        dtype = _attr.map_num_type_reversed[raw.dtype]
        return dtype, raw

    @classmethod
    def _save_binary(cls, path: str, value):
        _attr.np.save(path, value)
