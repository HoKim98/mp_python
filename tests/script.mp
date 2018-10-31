# ADD
    a1 = 3
    a2 = 4
    a3 = a1 + a2

    at = a3 == 7

# DISPOSABLE
    b1 = 1
    b1 := 2

    b2 := 1
    b2 = 2

    bt = (b1 == 1) * (b2 == 2)

# USER_DEFINED_METHOD
    c_mul = def(c1, c2, c1 * c2)
    c_pow = def(c3, c4, (c_mul * c4)(c3, 1))

    c5 = c_pow(2, 8)
    c5 += c_pow(3, 2)
    ct = (c5 == 265)

# PRINT
    _ = print(at, bt, ct)
    save _
