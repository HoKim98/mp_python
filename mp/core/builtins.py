_print = print


def array(toward, args):
    raise NotImplementedError


def print(toward, args):
    values = args.get_values()
    for arg, value in zip(args.list, values):
        output = '%s = %s' % (arg.symbol, value)
        _print(output)
    toward.is_data = False
    return None
