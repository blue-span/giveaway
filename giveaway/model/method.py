from collections import deque
import sys
import os
from pathlib import Path


__all__ = []


def _generate_methods(top):
    def method_factory(dir_entry):
        path = Path(dir_entry)
        assert path.suffix == ".sql"
        assert path.stem not in dir(sys.modules[__name__])
        with path.open() as fp:
            sql = fp.read().strip()
            setattr(sys.modules[__name__], path.stem, sql)
            __all__.append(path.stem)
    this_dir = Path(sys.modules[__name__].__file__)
    queries = filter(lambda d: d.is_file(), os.scandir(this_dir.parent / top))
    deque(map(method_factory, queries), maxlen=0)


_generate_methods("schema")
_generate_methods("query")
