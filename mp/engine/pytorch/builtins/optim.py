from mp.core import extension as _ext
from mp.engine.pytorch.attribute import torch as _torch

_F = _torch.optim


@_ext.static('__optim_adam', fixed=True)
def method_optim_adam(toward, args, plan):
    args.assert_sizeof(toward.symbol, 1)
    lr, = args.get_value()
    optim = _F.Adam({_torch.zeros(1)}, lr)
    return optim


@_ext.static('__optim_step')
def method_optim_step(toward, args, plan):
    args.assert_sizeof(toward.symbol, 2)
    args.list[1].remove_cache()
    optim, loss = args.get_value()
    optim.zero_grad()
    loss.backward()
    optim.step()
    return loss
