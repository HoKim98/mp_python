from hurry.filesize import size as _size
from mp.core.io import IO
from mp.utils.os_type import is_windows, is_linux

from mp.core import extension as _ext
from mp.core.expression import Expression as Exp
from mp.core.error import WWWNotFound

from mp.engine.python.attribute import map_num_type
from mp.engine.python.attribute import np as _np

import gzip
import os
import requests
import sys

CHUNK_SIZE = 4096


def _get_width():
    if is_windows():
        return 80
    #elif is_linux():
    return int(os.popen('stty size', 'r').read().split()[1])


def _www_download(name: str, url: str, filename: str):
    """
        Referred from https://stackoverflow.com/questions/566746/how-to-get-linux-console-window-width-in-python
    """

    print('[www] Downloading %s' % name)
    response = requests.get(url, stream=True)
    total_length = response.headers.get('content-length')

    with open(os.path.join(filename), 'wb') as f:
        # no content length header
        if total_length is None:
            f.write(response.content)
        # has content length header
        else:
            downloaded_length = 0
            total_length = int(total_length)
            print('[www] Total Size: %s' % _size(total_length))
            for data in response.iter_content(chunk_size=CHUNK_SIZE):
                downloaded_length += len(data)
                f.write(data)
                # update ratio
                ratio = str(int(downloaded_length / total_length * 100))
                # update downloaded file size
                filesize = '%s/%s' % (_size(downloaded_length), _size(total_length))
                # update progress bar
                bar_size = _get_width() - len(ratio) - len(filesize) - 6
                pointer = int(bar_size * downloaded_length / total_length)
                sys.stdout.write('\r|%s>%s| %s %s%%' % ('-' * pointer, ' ' * (bar_size - pointer), filesize, ratio))
                sys.stdout.flush()
            print()


def www(url: str, dataset_dir: str, filename: str, filetype: str, plan, force: bool = False):
    name = '%s.%s' % (dataset_dir, filename)
    path = os.path.join(IO.get_path(name, plan.io.dir_main))
    IO.make_dir_recursive(name.split('.'), plan.io.dir_main)
    filepath = '%s.%s' % (path, filetype)
    if not os.path.exists(filepath) or force:
        _www_download(name, url, filepath)
    return path


def decompress(name: str, path: str, filetype: str, num_type: str, shape=None, offset: int = 0):
    file_in = '%s.%s' % (path, filetype)
    file_out = '%s.%s' % (path, Exp.EXTENSION_BINARY)
    if os.path.exists(file_out):
        return

    print('[www] Decompressing %s' % name)
    if filetype in ['gz']:
        with gzip.open(file_in, 'rb') as f_in:
            dtype = map_num_type[num_type]
            raw = _np.frombuffer(f_in.read(), dtype, offset=offset)
            if shape is not None:
                raw = raw.reshape(*shape)
            _np.save(file_out, raw, allow_pickle=False)


@_ext.header('www', fixed=True)
def method_extern_www(toward, args, plan):
    name = str(toward)
    method, _ = plan.find_method(name)
    if method is not None:
        # must be hidden
        if method.hidden:
            return method.execute(toward, args, plan)
    raise WWWNotFound(name)
