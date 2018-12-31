from mp.core import extension as _ext


@_ext.static('tensor', fixed=True)
def method_tensor(plan, toward, args, kwargs):
    raise NotImplementedError


@_ext.static('if')
def method_if(plan, toward, args, kwargs):
    args.assert_sizeof(toward.symbol, 3)
    condition = bool(args.list[0].get_value())
    result = args.list[2 - int(condition)]
    result = result.get_value()
    return result


@_ext.static('repeat')
def method_repeat(plan, toward, args, kwargs):
    args.assert_sizeof(toward.symbol, 2)
    method, repeat = args.list
    repeat = repeat.get_value()
    for _ in range(int(repeat)):
        method.get_value()
    return None
