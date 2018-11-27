from mp.core import io
from mp.engine.pytorch.device import Device
from mp.engine.pytorch.framework import torch as _torch


class IO(io.IO):

    @classmethod
    def _load_binary_raw(cls, path):
        raw_np = super()._load_binary_raw(path)
        raw_torch = _torch.from_numpy(raw_np).to(Device.get())
        return raw_torch

    @classmethod
    def _save_binary(cls, path: str, value):
        # is PyTorch Tensor
        if type(value) is _torch.Tensor:
            raw_np = value.cpu().numpy()
        else:
            raw_np = io.np.array(value)
        super()._save_binary(path, raw_np)
