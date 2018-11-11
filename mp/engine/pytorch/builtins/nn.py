from mp.core import extension as _ext
from mp.engine.pytorch.attribute import torch as _torch

_F = _torch.nn.functional


@_ext.static('__nn_relu')
def method_nn_relu(toward, args):
    args.assert_sizeof(toward.symbol, 1)
    x, = args.get_values()
    x = _F.relu(x)
    return x


@_ext.static('__nn_conv1d')
def method_nn_conv1d(toward, args):
    args.assert_sizeof(toward.symbol, 2, +1)
    x, weight, *args = args.get_values()
    x = _F.conv1d(x, weight, *args)
    return x


@_ext.static('__nn_conv2d')
def method_nn_conv2d(toward, args):
    args.assert_sizeof(toward.symbol, 2, +1)
    x, weight, *args = args.get_values()
    x = _F.conv2d(x, weight, *args)
    return x
