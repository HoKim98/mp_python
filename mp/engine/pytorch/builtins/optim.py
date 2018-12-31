from mp.core import extension as _ext
from mp.engine.pytorch.framework import torch as _torch

_F = _torch.optim


@_ext.static('__optim_adam', fixed=True)
def method_optim_adam(plan, toward, args, kwargs):
    args.assert_sizeof(toward.symbol, 1)
    lr, = args.get_value()
    optim = _F.Adam({_torch.zeros(1)}, lr)
    return optim


def has_trainer_inited(plan):
    result = False
    for row in plan.event('has trainer'):
        result = result or row
    return result


@_ext.static('step')
def method_optim_step(plan, toward, args, kwargs):
    args.assert_sizeof(toward.symbol, 2)
    # init
    if not has_trainer_inited(plan):
        optim, loss_graph = args.list
        plan.event('get optim', optim.get_value())
        plan.event('get loss graph', loss_graph)
        # for events & init
        loss = loss_graph.get_value()
        return loss
    return None
