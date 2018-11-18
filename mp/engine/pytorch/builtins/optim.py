from mp.core import extension as _ext
from mp.engine.pytorch.attribute import torch as _torch

_F = _torch.optim


@_ext.static('__optim_adam', fixed=True)
def method_optim_adam(toward, args, plan):
    args.assert_sizeof(toward.symbol, 1)
    lr, = args.get_value()
    optim = _F.Adam({_torch.zeros(1)}, lr)
    return optim


def has_next_batch(plan):
    result = False
    for event in plan.event('has next batch'):
        result = result or event
    return result


@_ext.static('step')
def method_optim_step(toward, args, plan):
    args.assert_sizeof(toward.symbol, 2)
    # Init
    plan.event('reset batch')
    args.get_value()
    loss_sum = 0.
    count = 0
    # Begin training
    while has_next_batch(plan):
        args.list[1].remove_cache()
        optim, loss = args.get_value()
        loss_sum += float(loss)
        optim.zero_grad()
        loss.backward()
        optim.step()
        # add count
        count += 1
    # get loss
    if count == 0:
        return None
    return loss_sum / count
