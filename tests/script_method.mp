# CORE
    k = tensor(1)
    k += rand(1)
    k += randn(1)
    k = float(k)
    k = long(k)

# MATH
    a1 = 0. - 1.

    a2 = __abs(a1 * 3.14)
    at = a2 == 3.14

# REDUCE
    b1 = max(3., 4.)  # 4
    b2 = min(3., 4.)  # 3

    b3 = tensor(3, 4) + 1.

    b4 = sum(b3)  # 12
    b5 = mean(b3)  # 1
    b5 = b1 + b2 + b4 + b5  # 20
    bt = long(b5) == 20

    print at, bt, k
