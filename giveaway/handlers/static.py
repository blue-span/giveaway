import h11
from itertools import chain, starmap, repeat
from os import path, walk
from pathlib import Path

from giveaway.http.server import FilePassthrough


content_types = {
    ".png": b"image/png",
    ".css": b"text/css",
    ".html": b"text/html",
}

default_content_type = b"application/octet-stream"


def walk_files(topdir):
    def files(dirpath, _dirnames, filenames):
        return zip(repeat(dirpath), filenames)
    return chain.from_iterable(starmap(files, walk(topdir)))


def routes(topdir="static"):
    def as_route(dirpath, filepath):
        return ((b"GET", path.join("/", dirpath, filepath).encode("utf-8")), request_handler)
    return starmap(as_route, walk_files(topdir))


def request_handler(event_generator):
    request = next(event_generator, None)
    if not isinstance(request, h11.Request):
        return

    path = Path(request.target[len(b"/"):].decode("utf-8"))
    data = FilePassthrough(path)

    yield h11.Response(
        status_code=200,
        headers=[
            (b"content-type", content_types.get(path.suffix, default_content_type)),
            (b"content-length", str(len(data)).encode("utf-8")),
        ]
    )

    yield h11.Data(data=data)
