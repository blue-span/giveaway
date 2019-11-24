import h11
from functools import partial, update_wrapper
from itertools import chain, starmap, repeat
from os import path, walk
from pathlib import Path

from giveaway.http.server import FilePassthrough


content_types = {
    ".png": b"image/png",
    ".css": b"text/css",
    ".html": b"text/html",
    ".mjs": b"application/javascript",
}

default_content_type = b"application/octet-stream"


def walk_files(topdir):
    def files(dirpath, _dirnames, filenames):
        return zip(repeat(dirpath), filenames)
    return chain.from_iterable(starmap(files, walk(topdir)))


def make_routes(topdir, base_url_path, strip_stem=None):
    def as_route(dirpath, filepath):
        path = (Path(dirpath) / filepath).absolute()
        if ".py" in path.suffix:
            return
        else:
            url_path = Path(base_url_path) / path.relative_to(topdir)
            target = (
                url_path.parent
                if strip_stem is not None and strip_stem == url_path.stem
                else url_path
            )
            handler = lambda eg: get(eg, path=path)
            return ((b"GET", str(target).encode("utf-8")), update_wrapper(handler, get))
    return filter(lambda r: r is not None, starmap(as_route, walk_files(topdir)))


def get(event_generator, path):
    request = next(event_generator, None)
    if not isinstance(request, h11.Request):
        return

    data = FilePassthrough(path)

    yield h11.Response(
        status_code=200,
        headers=[
            (b"content-type", content_types.get(path.suffix, default_content_type)),
            (b"content-length", str(len(data)).encode("utf-8")),
        ]
    )

    yield h11.Data(data=data)
