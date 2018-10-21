_print = print


def array(toward, args):
    raise NotImplementedError


def print(toward, args):
    values = args.get_values()
    for arg, value in zip(args.list, values):
        if arg.is_constant:
            _print('%s = %s' % (arg.symbol, value))
            continue
        output = '%s = %s %s' % (arg.symbol, value, arg.code)
        _print(output)
    toward.is_data = False
    return None
