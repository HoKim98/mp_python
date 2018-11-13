from mp.core import extension as _ext


@_ext.static('tensor', fixed=True)
def method_tensor(toward, args, plan):
    raise NotImplementedError


@_ext.static('if')
def method_if(toward, args, plan):
    args.assert_sizeof(toward.symbol, 3)
    condition = bool(args.list[0].get_value())
    result = args.list[2 - int(condition)]
    result = result.get_value()
    return result


@_ext.static('repeat')
def method_repeat(toward, args, plan):
    args.assert_sizeof(toward.symbol, 2)
    method, repeat = args.list
    repeat = repeat.get_value()
    for _ in range(int(repeat)):
        method.get_value()
    return None
