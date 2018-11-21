# 데이터셋 준비
    train x = float(www.mnist.train.images) / 255.
    train y = long(www.mnist.train.labels)

# 미니배치 준비
    train x = batch(train x, 50)
    train y = batch(train y, 50)

    #train x = batch(shuffle(train x), 50)
    #train y = batch(shuffle(train y), 50)

# 최적화 도구
    optim = Adam()

# 컨볼루션 가중치
    weight conv 1 = var(randn(32, 1, 5, 5), optim)
    weight conv 2 = var(randn(64, 32, 5, 5), optim)
    bias conv 1 = var(randn(32), optim)
    bias conv 2 = var(randn(64), optim)

# 행렬곱 가중치
    weight dense 1 = var(randn(1024, 64 * 7 * 7), optim)
    weight dense 2 = var(randn(10, 1024), optim)
    bias dense 1 = var(randn(1024), optim)
    bias dense 2 = var(randn(10), optim)

# 컨볼루션 2번
    output = relu(conv2d(train x, weight conv 1, bias conv 1, _stride=2, _padding=2))
    output = relu(conv2d(output, weight conv 2, bias conv 2, _stride=2, _padding=2))

# 행렬곱 2번
    output = output[50, 64 * 7 * 7]
    output = relu(dense(output, weight dense 1, bias dense 1))
    output = dense(output, weight dense 2, bias dense 2)

# 오차함수
    loss = cross entropy(output, train y)

# 1회 훈련
    trainer = step(optim, loss)

# 반복 훈련 및 모니터링
    num epochs = 1
    monitor = trace(trainer, num epochs)
    print monitor
