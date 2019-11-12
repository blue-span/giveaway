from functools import partial
import socket
import sys

from giveaway.http import server
from giveaway import router


def main():
    address = ('::', 8080)
    handler = partial(server.http_stream_handler, request_handler=router.request_handler)
    http = server.TCPServer(address, handler)
    print(f"{address=}", file=sys.stdout)
    http.serve_forever()


main()
