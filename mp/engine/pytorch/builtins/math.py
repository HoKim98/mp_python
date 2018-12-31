from mp.core import extension as _ext


@_ext.static('abs')
def method_math_abs(plan, toward, args, kwargs):
    args.assert_sizeof(toward.symbol, 1)
    x, = args.get_value()
    x = x.abs()
    return x


map_op = {
    '__math_add': lambda x, y: x + y,
    '__math_sub': lambda x, y: x - y,
    '__math_mul': lambda x, y: x * y,
    '__math_tdiv': lambda x, y: x / y,
    '__math_mat': lambda x, y: x @ y,
    '__math_pow': lambda x, y: x ** y,
    '__math_fdiv': lambda x, y: x // y,
    '__math_mod': lambda x, y: x % y,

    '__math_eq': lambda x, y: x == y,
    '__math_neq': lambda x, y: x != y,
    '__math_gt': lambda x, y: x > y,
    '__math_ge': lambda x, y: x >= y,
    '__math_lt': lambda x, y: x < y,
    '__math_le': lambda x, y: x <= y,
}


# add into module
for name, op in map_op.items():
    _ext.binary(name, op, scope=globals())
del map_op
