# Default value
    true = 1b
    false = 0b
    none = 0b

# Activation Methods
    relu = def(_x, __nn_relu(_x))

# Convolution Methods
    conv1d = def(_x, _w, _bias=none, _stride=1, _padding=0, _dilation=1, __nn_conv1d(_x, _w, _bias, _stride, _padding, _dilation))
    conv2d = def(_x, _w, _bias=none, _stride=1, _padding=0, _dilation=1, __nn_conv2d(_x, _w, _bias, _stride, _padding, _dilation))

# Optimizers
    Adam = def(_lr = 1e-3, __optim_adam(_lr))

# Dataset
    shuffle = def(_x, _dim=0, __dataset_shuffle(_x, _dim))
