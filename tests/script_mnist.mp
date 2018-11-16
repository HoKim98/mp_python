    _y = mean(__abs(_x))
    mean absolute error = def(_x, _y)

    _y = mean((_x - 0.) ** 2.)
    mean square error = def(_x, _y)

    train x = float(www.mnist.train.images)(:100) / 255.
    train y = float(www.mnist.train.labels)

    optim = Adam(_lr=1e-1)

    weight conv 1 = var(randn(32, 1, 5, 5), optim)
    weight conv 2 = var(randn(64, 32, 5, 5), optim)
    bias conv 1 = var(randn(32), optim)
    bias conv 2 = var(randn(64), optim)

    output = relu(conv2d(input, weight conv 1, bias conv 1, _stride=2, _padding=2))
    output = relu(conv2d(output, weight conv 2, bias conv 2, _stride=2, _padding=2))
    loss = mean square error(output)

    one step = def(input, feedback, step(optim, loss))
    one epoch = (one step * 20)(train x, none)
    print one epoch
