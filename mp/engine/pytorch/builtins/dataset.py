from math import ceil

from mp.core import extension as _ext
from mp.engine.pytorch.framework import torch as _torch


class DatasetBatch:
    def __init__(self, code, args):
        self.code = code
        self.args = args

        self.iter = 0
        self.origin = None
        self.batch_size = 0
        self.length = 0
        self.reset()

    def _get_indices(self):
        begin = self.iter
        end = min(self.iter + self.batch_size, self.length)
        return slice(begin, end)

    def _update_iter(self):
        self.iter += self.batch_size

    def next(self):
        indices = self._get_indices()
        self._update_iter()
        return self.origin[indices]

    # ------------ For Events -------------------------------

    def has_next(self):
        return self.iter < self.length

    def reset(self):
        self.iter = 0
        self.args.remove_cache()
        self.origin, batch_size = self.args.get_value()
        self.batch_size = int(batch_size)
        self.length = self.origin.shape[0]
        return self.code

    def __len__(self):
        return ceil(self.length / self.batch_size)


@_ext.static('batch')
def method_dataset_batch(plan, toward, args, kwargs):
    # Find registered method
    code = str(toward)
    method = plan.event(code)
    if len(method) > 0:
        return method[0]
    # Prepare a new method.
    args.assert_sizeof(toward.symbol, 2)
    method = DatasetBatch(code, args)
    # Register the method in the event management class.
    plan.event.add(code, method.next)
    plan.event.add('has next batch', method.has_next)
    plan.event.add('reset batch', method.reset)
    plan.event.add('get batch length', method.__len__)
    return method.next()


@_ext.static('__dataset_shuffle')
def method_dataset_shuffle(plan, toward, args, kwargs):
    args.assert_sizeof(toward.symbol, 2)
    x, dim = args.get_value()
    dim = int(dim)
    group = [slice(None) for _ in range(dim)]
    indices = _torch.randperm(x.shape[dim])
    x = x[group + [indices]]
    return x
