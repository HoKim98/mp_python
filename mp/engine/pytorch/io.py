from mp.engine.python.io import IO as _IO
from mp.engine.pytorch import attribute as _attr
from mp.engine.pytorch.device import Device


class IO(_IO):

    @classmethod
    def _load_binary_raw(cls, path):
        raw_np = super()._load_binary_raw(path)
        raw_torch = _attr.torch.from_numpy(raw_np).to(Device.get())
        return raw_torch

    @classmethod
    def _save_binary(cls, path: str, value):
        raw_np = value.cpu().numpy()
        super()._save_binary(path, raw_np)
