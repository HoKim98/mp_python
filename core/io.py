import os

from core.expression import Expression as Exp
from core.data import Constant


class IO:

    def __init__(self, dir_main: str, permission: int = 0o775):
        if len(dir_main) == 0:
            dir_main = os.path.curdir
        self.dir_main = '%s/%s' % (os.path.curdir, dir_main)
        self.permission = permission

    def get(self, item: str):
        path = self.get_path(item)
        # is graph file
        path_graph = self._get_graph_path(path)
        if os.path.exists(path_graph):
            return self._load_graph(path_graph)
        # is binary file
        path_binary = self._get_binary_path(path)
        if os.path.exists(path_binary):
            return self._load_binary(item, path_binary)
        # not found
        return None

    def set(self, item: str, toward):
        paths = item.split('.')
        # if toward is None -> remove file
        if toward is None:
            path_graph = '%s.%s' % (self.get_path(item), Exp.EXTENSION_SOURCE)
            path_graph = os.path.join(self.dir_main, path_graph)
            if os.path.exists(path_graph):
                self._remove(path_graph)
            self._remove_dirs(paths)
            path_binary = '%s.%s' % (self.get_path(item), Exp.EXTENSION_BINARY)
            path_binary = os.path.join(self.dir_main, path_binary)
            if os.path.exists(path_binary):
                self._remove(path_binary)
                self._remove_dirs(paths)
        # if toward is constant
        elif toward.is_constant:
            path = '%s.%s' % (self.get_path(item), Exp.EXTENSION_BINARY)
            path = os.path.join(self.dir_main, path)
            self._make_dir_recursive(paths)
            self._save_binary(path, toward.get_value())
        # if toward consists of graph
        else:
            path = '%s.%s' % (self.get_path(item), Exp.EXTENSION_SOURCE)
            path = os.path.join(self.dir_main, path)
            self._make_dir_recursive(paths)
            self._save_graph(path, toward.code)

    @classmethod
    def _load_binary_raw(cls, path):
        raise NotImplementedError

    @classmethod
    def _load_binary(cls, name: str, path: str):
        if os.path.exists(path):
            with open(path, 'rb') as f:
                num_type, value = cls._load_binary_raw(f)
                const = Constant(name, num_type, value)
            return const
        return None

    @classmethod
    def _load_graph(cls, path: str):
        if os.path.exists(path):
            with open(path, 'r') as f:
                msg = f.read()
            return msg
        return None

    @classmethod
    def _save_binary(cls, path: str, value):
        raise NotImplementedError

    @classmethod
    def _save_graph(cls, path: str, code: str):
        with open(path, 'w') as f:
            f.write(code)

    @classmethod
    def _remove(cls, path: str):
        os.remove(path)

    def _remove_dirs(self, paths):
        paths = paths[:-1]
        for i in range(len(paths), 0, -1):
            path = self.dir_main
            for dir_to in paths[:i]:
                path = os.path.join(path, dir_to)
            num_files = len(os.listdir(path))
            # if dir is empty
            if os.path.isdir(path) and num_files == 0:
                os.rmdir(path)
            else:
                break

    def _get_binary_path(self, path: str):
        path = '%s.%s' % (path, Exp.EXTENSION_BINARY)
        path = os.path.join(self.dir_main, path)
        return path

    def _get_graph_path(self, path: str):
        path = '%s.%s' % (path, Exp.EXTENSION_SOURCE)
        path = os.path.join(self.dir_main, path)
        return path

    def _make_dir_recursive(self, paths):
        path = self.dir_main
        for dir_name in paths[:-1]:
            path = os.path.join(path, dir_name)
            if not os.path.exists(path):
                os.mkdir(path, mode=self.permission)

    @classmethod
    def get_path(cls, filename, dir_from=None):
        filename = '/'.join(filename.split('.'))
        if dir_from is None:
            return filename
        dir_from = '/'.join(dir_from.split('.'))
        return os.path.join(dir_from, filename)
