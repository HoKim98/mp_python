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

# PRINT
    _ = print(at, bt)
    save _
