from tqdm import tqdm

from mp.core import extension as _ext
from mp.core import framework
from mp.core.expression import Expression as Exp
from mp.core.error import WWWNotFound, WWWNotInCandidate
from mp.core.io import IO

from mp.core.framework import np as _np

import gzip
import os
import requests

CHUNK_SIZE = 4096


class ContentLoader:
    def __init__(self, url: str):
        self.url = url
        self.response = requests.get(url, stream=True)
        # get content length
        self._total_length = self.response.headers.get('content-length')
        self._total_length = None if self._total_length is None else int(self._total_length)
        # iteration
        self._iter = self.response.iter_content(chunk_size=CHUNK_SIZE)
        self._tqdm = tqdm(unit_divisor=1024, unit_scale=True, total=len(self))

    def __next__(self):
        try:
            data = next(self._iter)
            self._tqdm.update(len(data))
            return data
        except StopIteration as e:
            self._close()
            raise e

    def __len__(self):
        return self._total_length

    def __iter__(self):
        return self

    def _close(self):
        self._tqdm.close()


def _www_download(name: str, url: str, filename: str):
    print('[www] Downloading %s' % name)
    with open(os.path.join(filename), 'wb') as f:
        for data in ContentLoader(url):
            f.write(data)


def www(url: str, dataset_dir: str, filename: str, filetype: str, plan, force: bool = False):
    name = '%s.%s' % (dataset_dir, filename)
    path = os.path.join(IO.get_path(name, plan.io.dir_main))
    IO.make_dir_recursive(name.split('.'), plan.io.dir_main)
    filepath = '%s.%s' % (path, filetype)
    if not os.path.exists(filepath) or force:
        _www_download(name, url, filepath)
    return path


def decompress(plan, name: str, path: str, filetype: str, num_type: str, shape=None, offset: int = 0):
    file_in = '%s.%s' % (path, filetype)
    file_out = '%s.%s' % (path, Exp.EXTENSION_BINARY)
    if os.path.exists(file_out):
        return

    print('[www] Decompressing %s' % name)
    if filetype in ['gz']:
        with gzip.open(file_in, 'rb') as f_in:
            dtype = framework.MAP_NUM_TYPE[num_type]
            raw = _np.frombuffer(f_in.read(), dtype, offset=offset)
            if shape is not None:
                raw = raw.reshape(*shape)
            _np.save(file_out, raw, allow_pickle=False)


@_ext.header('www', fixed=True)
def method_extern_www(plan, toward, args, kwargs):
    name = str(toward).replace(Exp.SHELL_RR[0], '')
    method = plan.event.find(name, hidden=True)
    if method is not None:
        # must be hidden
        if method.hidden:
            # must be in candidate
            filename = name.split('%s.' % method.base_dir)[1]
            if filename not in method.candidates:
                raise WWWNotInCandidate(name, method.base_dir, method.candidates)
            return method(plan, name, filename, args)
    raise WWWNotFound(name)
