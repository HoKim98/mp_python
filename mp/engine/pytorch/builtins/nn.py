from mp.core import extension as _ext
from mp.engine.pytorch.attribute import torch as _torch

_F = _torch.nn.functional


def _int_or_tuple(value):
    if type(value) is list:
        return value
    return int(value)


@_ext.static('__nn_relu')
def method_nn_relu(toward, args, plan):
    args.assert_sizeof(toward.symbol, 1)
    x, = args.get_value()
    x = _F.relu(x)
    return x


@_ext.static('__nn_conv1d')
def method_nn_conv1d(toward, args, plan):
    args.assert_sizeof(toward.symbol, 6)
    x, weight, bias, stride, padding, dilation = args.get_value()
    bias = args.assert_false_to_none(bias)
    x = _F.conv1d(x, weight, bias, _int_or_tuple(stride), int(padding), int(dilation))
    return x


@_ext.static('__nn_conv2d')
def method_nn_conv2d(toward, args, plan):
    args.assert_sizeof(toward.symbol, 6)
    x, weight, bias, stride, padding, dilation = args.get_value()
    bias = args.assert_false_to_none(bias)
    x = _F.conv2d(x, weight, bias, _int_or_tuple(stride), int(padding), int(dilation))
    return x
