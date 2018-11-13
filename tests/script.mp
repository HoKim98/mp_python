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

    c5 = c_pow(2, 8) - c_pow(3, 2)
    c5 -= c_pow(1, 1)
    ct = (c5 == 246)

# IF
    d1 = 3
    d2 = 4
    d3 = if(d1 == d2, 5, 6)
    dt = d3 == 6

# INDICES & VIEW
    e1 = tensor(3, 4, 5)
    e2 = e1(:, 2:, 1::2)()
    e3 = e2{}
    e4 = e2{2}
    e5 = e1{1, 0}{0}
    et = (e3 == 3) * (e4 == 2) * (e5 == 4)

# SELF
    self.f1 = 3.14
    ft = self.f1 == script.f1

# PRINT
    print at, bt, ct, dt, et, ft
