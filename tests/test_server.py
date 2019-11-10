
def request_handler(events):
    import threading
    print(threading.current_thread())
    import time
    time.sleep(5)
    return [
        h11.Response(status_code=200, headers=[]),
        h11.Data(data=b"hello\n"),
        h11.EndOfMessage(),
    ]


http = TCPServer(('127.0.0.1',8000), partial(http_stream_handler, request_handler=request_handler))
try:
    http.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    http.server_close()
