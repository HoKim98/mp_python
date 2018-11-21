# Default value
    true = 1b
    false = 0b
    none = 0b

# Typical Layers
    dense = def(_x, _w, _bias=none, __nn_dense(_x, _w, _bias))

# Loss Functions
    cross entropy = def(_x, _y, __nn_cross_entropy(_x, _y))

# Activation Functions
    sigmoid = def(_x, __nn_sigmoid(_x))
    tanh = def(_x, __nn_tanh(_x))
    softmax = def(_x, _dim=none, __nn_softmax(_x, _dim))
    relu = def(_x, __nn_relu(_x))

# Convolution Layers
    conv1d = def(_x, _w, _bias=none, _stride=1, _padding=0, _dilation=1, __nn_conv1d(_x, _w, _bias, _stride, _padding, _dilation))
    conv2d = def(_x, _w, _bias=none, _stride=1, _padding=0, _dilation=1, __nn_conv2d(_x, _w, _bias, _stride, _padding, _dilation))

# Optimizers
    Adam = def(_lr = 1e-3, __optim_adam(_lr))

# Dataset
    shuffle = def(_x, _dim=0, __dataset_shuffle(_x, _dim))
