from functools import partial
import os
import socket
import sys
import threading

from giveaway.http import server
from giveaway import router
from giveaway import database


http_port = os.environ.get("BLUESPAN_HTTP_PORT", 8081)
https_port = os.environ.get("BLUESPAN_HTTPS_PORT", 8080)


def http_main():
    address = ('::', http_port)
    handler = partial(server.http_stream_handler, request_handler=router.https_handler)
    http = server.ThreadingTCPServer(address, handler)
    print(f"http {address=}", file=sys.stdout)
    http.serve_forever()


def https_main():
    address = ('::', https_port)
    handler = partial(server.http_stream_handler, request_handler=router.request_handler)
    http = server.ThreadingTLSServer(address, handler)
    print("\n".join(repr(i) for i in sorted(
        map(lambda kv: (kv[0], router.handler_name(kv[1])), router.routes.items()),
        key=lambda kv: (kv[0][1], kv[0][0])
    )))

    assert database.database_path().stat().st_size > 0, "initialize database"

    print(f"https {address=}", file=sys.stdout)
    http.serve_forever()


def main():
    http_thread = threading.Thread(target=http_main)
    https_thread = threading.Thread(target=https_main)

    http_thread.start()
    https_thread.start()

    # fate sharing? I honestly don't care at this point
    https_thread.join()


if __name__ == "__main__":
    main()
