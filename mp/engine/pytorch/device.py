from mp.engine.pytorch.framework import torch as _torch


class Device:
    get = None

    def __init__(self, use_cuda: bool):
        self._device = _torch.device('cuda' if use_cuda else 'cpu')
        self.__class__.get = self

    def __call__(self):
        return self._device
