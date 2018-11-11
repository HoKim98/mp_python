# Activation Methods
    relu = def(relu_x, __nn_relu(relu_x))

# Convolution Methods
    conv1d = def(conv1d_x, conv1d_w, __nn_conv1d(conv1d_x, conv1d_w))
    conv2d = def(conv2d_x, conv2d_w, __nn_conv2d(conv2d_x, conv2d_w))

# Optimizers
    Adam = def(adam_lr = 1e-3, __optim_adam(adam_lr))

    step = def(step_optim, step_loss, __optim_step(step_optim, step_loss))
