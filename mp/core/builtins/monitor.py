from tqdm import tqdm

from mp.core import extension as _ext


class Monitor:
    def __init__(self, args, plan):
        self.args = args
        self.plan = plan
        self.plan.event.add('next step', self.next_step)

        self._name = self.args.list[0].symbol
        self._tqdm = None
        self._length = None

    def begin(self):
        for _ in range(self.get_num_epochs()):
            self.begin_epoch()
            self.args.list[0].remove_cache()
            loss = self.args.list[0].get_value()
            self.end_epoch(loss)
        return None

    def get_num_epochs(self):
        if len(self.args.list) >= 2:
            return int(self.args.list[1].get_value())
        return 1

    def get_batch_length(self):
        minimum = None
        for length in self.plan.event('get batch length'):
            minimum = min(minimum, length) if minimum is not None else length
        return minimum

    def update_batch_length(self):
        if self._length is None:
            self._length = self.get_batch_length()
            self._tqdm.total = self._length

    def begin_epoch(self):
        self._tqdm = tqdm(desc=self._name, total=self.get_batch_length())
        self._tqdm.update()

    def end_epoch(self, loss):
        self._tqdm.close()
        print('Loss:', loss)

    # ------------ For Events -------------------------------

    def next_step(self, trainer, loss):
        self.update_batch_length()
        self._tqdm.update()


@_ext.static('trace')
def method_trace(toward, args, plan):
    args.assert_sizeof(toward.symbol, 1, +1)
    monitor = Monitor(args, plan)
    loss = monitor.begin()
    return loss
