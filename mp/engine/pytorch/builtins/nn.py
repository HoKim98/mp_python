from mp.core import extension as _ext
from mp.engine.pytorch.framework import torch as _torch

_F = _torch.nn.functional


def _int_or_tuple(value):
    if type(value) is list:
        return value
    return int(value)

# -----------------------------
# Typical Layers
# -----------------------------


@_ext.static('__nn_dense')
def method_nn_dense(plan, toward, args, kwargs):
    args.assert_sizeof(toward.symbol, 3)
    x, weight, bias = args.get_value()
    bias = args.assert_false_to_none(bias)
    x = _F.linear(x, weight, bias)
    return x

# -----------------------------
# Loss Functions
# -----------------------------


@_ext.static('__nn_cross_entropy')
def method_nn_cross_entropy(plan, toward, args, kwargs):
    args.assert_sizeof(toward.symbol, 2)
    x, y = args.get_value()
    x = _F.cross_entropy(x, y)
    return x

# -----------------------------
# Activation Functions
# -----------------------------


@_ext.static('__nn_sigmoid')
def method_nn_sigmoid(plan, toward, args, kwargs):
    args.assert_sizeof(toward.symbol, 1)
    x, = args.get_value()
    x = x.sigmoid()
    return x

@_ext.static('__nn_tanh')
def method_nn_tanh(plan, toward, args, kwargs):
    args.assert_sizeof(toward.symbol, 1)
    x, = args.get_value()
    x = x.tanh()
    return x

@_ext.static('__nn_softmax')
def method_nn_softmax(plan, toward, args, kwargs):
    args.assert_sizeof(toward.symbol, 2)
    x, dim = args.get_value()
    dim = args.assert_false_to_none(dim)
    dim = dim if dim is not None else -1
    x = x / 100.
    x = _F.softmax(x, dim)
    return x

@_ext.static('__nn_relu')
def method_nn_relu(plan, toward, args, kwargs):
    args.assert_sizeof(toward.symbol, 1)
    x, = args.get_value()
    x = _F.relu(x)
    return x

# -----------------------------
# Convolution Layers
# -----------------------------


@_ext.static('__nn_conv1d')
def method_nn_conv1d(plan, toward, args, kwargs):
    args.assert_sizeof(toward.symbol, 6)
    x, weight, bias, stride, padding, dilation = args.get_value()
    bias = args.assert_false_to_none(bias)
    x = _F.conv1d(x, weight, bias, _int_or_tuple(stride), int(padding), int(dilation))
    return x


@_ext.static('__nn_conv2d')
def method_nn_conv2d(plan, toward, args, kwargs):
    args.assert_sizeof(toward.symbol, 6)
    x, weight, bias, stride, padding, dilation = args.get_value()
    bias = args.assert_false_to_none(bias)
    x = _F.conv2d(x, weight, bias, _int_or_tuple(stride), int(padding), int(dilation))
    return x
