    _y = mean(__abs(_x))
    mean absolute error = def(_x, _y)

    _y = mean((_x - 0.) ** 2.)
    mean square error = def(_x, _y)

    train x = float(www.mnist.train.images) / 255.
    train y = float(www.mnist.train.labels)

    train x = batch(shuffle(train x), 50)

    optim = Adam(_lr=1e-1)

    weight conv 1 = var(randn(32, 1, 5, 5), optim)
    weight conv 2 = var(randn(64, 32, 5, 5), optim)
    bias conv 1 = var(randn(32), optim)
    bias conv 2 = var(randn(64), optim)

    output = relu(conv2d(train x, weight conv 1, bias conv 1, _stride=2, _padding=2))
    output = relu(conv2d(output, weight conv 2, bias conv 2, _stride=2, _padding=2))
    loss = mean square error(output)

    num_train = 1

    trainer = (step * num_train)(optim, loss)
    print trainer
