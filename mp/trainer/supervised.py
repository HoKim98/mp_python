from mp.core.expression import Expression as Exp


class StandardTrainer:
    def __init__(self):
        self._optim = None
        self._loss_graph = None

        Exp.EVENT.add('get optim', self._get_optim, unique=True)
        Exp.EVENT.add('get loss graph', self._get_loss_graph, unique=True)
        Exp.EVENT.add('has trainer inited', self._alive)

    def one_epoch(self):
        Exp.EVENT('reset batch')
        loss_sum = 0.
        count = 0
        # Begin training
        while self._has_next_batch():
            self._loss_graph.remove_cache()
            loss = self._loss_graph.get_value()
            loss_sum += float(loss)
            self._optim.zero_grad()
            loss.backward()
            self._optim.step()
            # add count
            count += 1
            # Transfer status to monitor
            Exp.EVENT('next step', self, float(loss))
        # get loss
        if count == 0:
            return None
        return loss_sum / count

    def _get_optim(self, optim):
        Exp.EVENT.remove('get optim')
        self._optim = optim

    def _get_loss_graph(self, loss_graph):
        Exp.EVENT.remove('get loss graph')
        self._loss_graph = loss_graph

    def _alive(self):
        return self._optim is not None and self._loss_graph is not None

    @classmethod
    def _has_next_batch(cls):
        result = False
        for event in Exp.EVENT('has next batch'):
            result = result or event
        return result
