from mp.engine.python.io import IO as _IO
from mp.engine.python.io import _attr as _attr_python
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
        # is PyTorch Tensor
        if type(value) is _attr.torch.Tensor:
            raw_np = value.cpu().numpy()
        else:
            raw_np = _attr_python.np.array(value)
        super()._save_binary(path, raw_np)
