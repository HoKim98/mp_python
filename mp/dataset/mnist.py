"""
    Download and preprocess MNIST dataset from 'http://yann.lecun.com/exdb/mnist'
"""
from mp.core import extension as _ext
from mp.core.error import WWWNotInCandidate

from mp.dataset.core import decompress as _decompress
from mp.dataset.core import www as _www

FILE_TYPE = 'gz'
BASE_DIR = 'www.mnist'
URL_BASE = 'http://yann.lecun.com/exdb/mnist'
MAP_MNIST = {
    'train.images': '%s/train-images-idx3-ubyte.gz' % URL_BASE,
    'train.labels': '%s/train-labels-idx1-ubyte.gz' % URL_BASE,
    'test.images': '%s/t10k-images-idx3-ubyte.gz' % URL_BASE,
    'test.labels': '%s/t10k-labels-idx1-ubyte.gz' % URL_BASE,
}

DATA_TYPE = 'i8'
SHAPE_MNIST = {
    'train.images': (-1, 1, 28, 28),
    'train.labels': None,
    'test.images': (-1, 1, 28, 28),
    'test.labels': None,
}
OFFSET_MNIST = {
    'train.images': 16,
    'train.labels': 8,
    'test.images': 16,
    'test.labels': 8,
}


@_ext.dataset(BASE_DIR, MAP_MNIST.keys())
def method_dataset_mnist(plan, name, filename, args):
    url = MAP_MNIST[filename]
    path = _www(url, BASE_DIR, filename, FILE_TYPE, plan)
    shape = SHAPE_MNIST[filename]
    offset = OFFSET_MNIST[filename]
    _decompress(plan, name, path, FILE_TYPE, DATA_TYPE, shape, offset=offset)
    return plan.io.get(name)
