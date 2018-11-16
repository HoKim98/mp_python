from argparse import ArgumentParser
import requests

from mp.utils import environment as env


PYTORCH_URL = 'https://pytorch.org/assets/quick-start-module.js'
PYTORCH_CUDA = {
    '8.0': '8',
    '9.0': '9.0',
    '9.2': '9.2',
    'none': 'none',
}


# Works fine on 2018-11-16.
def get_pytorch(package: str = 'pip', cuda: str = 'cudanone', build: str = 'stable'):
    your_os = env.get_os()
    python = env.get_python_version()
    key = ','.join([build, package, your_os, 'cuda%s' % cuda, 'python%s' % python]).encode()

    result = requests.get(PYTORCH_URL).content
    idx = result.find(key)
    # not found
    if idx < 0:
        return
    # get command
    begin = result.find(b' "', idx) + 2
    end = result.find(b'",', begin)
    cmd = result[begin: end]
    # dismiss torchvision
    cmd = cmd.split(b'<br/>')[0]
    # pip3 -> pip
    cmd = cmd.replace(b'pip3', b'pip')
    print(cmd.decode())


if __name__ == '__main__':
    parser = ArgumentParser(prog='dependency', usage='%(prog)s [options]')
    parser.add_argument('-p', '--platform', default='pytorch', choices=['pytorch', ])
    parser.add_argument('-c', '--cuda', default='none', choices=PYTORCH_CUDA.keys())
    parser.add_argument('--package', default='pip', choices=['pip', 'conda', ])
    args = parser.parse_args()

    if args.platform == 'pytorch':
        get_pytorch(args.package, PYTORCH_CUDA[args.cuda], )
