from mp.core.builtins_decorator import extension


@extension.static('array')
def method_array(toward, args):
    raise NotImplementedError


@extension.static('if')
def method_if(toward, args):
    args.assert_sizeof(toward.symbol, 3)
    condition = bool(args.list[0].get_value())
    result = args.list[2 - int(condition)]
    result = result.get_value()
    return result
