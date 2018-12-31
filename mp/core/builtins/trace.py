from mp.core import extension as _ext


@_ext.static('trace')
def method_trace(plan, toward, args, kwargs):
    args.assert_sizeof(toward.symbol, 1, +1)
    plan.event('init monitor', args)
    loss = plan.event('begin training')
    return loss
