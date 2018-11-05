from mp.core.io import IO as _IO
from mp.engine.pytorch import attribute as _attr


class IO(_IO):

    @classmethod
    def _load_binary_raw(cls, path):
        raw = _attr.torch.load(path)
        dtype = _attr.map_num_type_reversed[raw.dtype]
        return dtype, raw

    @classmethod
    def _save_binary(cls, path: str, value):
        _attr.torch.save(path, value)
