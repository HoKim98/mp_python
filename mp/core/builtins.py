def __array(toward, args):
    raise NotImplementedError


def __print(toward, args):
    values = args.get_values()
    for arg, value in zip(args.list, values):
        if arg.is_constant:
            print('%s = %s' % (arg.symbol, value))
            continue
        output = '%s = %s %s' % (arg.symbol, value, arg.code)
        print(output)
    toward.is_data = False
    return None


def __if(toward, args):
    args.assert_sizeof(toward.symbol, 3)
    condition = bool(args.list[0].get_value())
    result = args.list[2 - int(condition)]
    result = result.get_value()
    return result
