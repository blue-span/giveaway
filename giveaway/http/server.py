from collections import namedtuple
from functools import partial
from pathlib import Path
import socketserver
import socket
import ssl
import sys

import h11


def acme_sni_callback(socket, server_name, original_context):
    print(socket, server_name, original_context)
    print(socket.context)
    new_context = tls_context()
    new_context.load_cert_chain('../certificate.pem', '../key.pem')
    socket.context = new_context
    print("cert loaded")


def tls_context():
    tls_context = ssl.create_default_context()
    tls_context.verify_mode = ssl.CERT_OPTIONAL
    tls_context.check_hostname = False
    #tls_context.sni_callback = acme_sni_callback
    tls_context.load_cert_chain('../certificate.pem', '../key.pem')
    return tls_context


class TCPServer(socketserver.TCPServer):
    allow_reuse_address = True
    address_family = socket.AF_INET6

    def get_request(self):
        stream, address = self.socket.accept()
        tls_stream = tls_context().wrap_socket(stream, server_side=True)
        return tls_stream, address


class ThreadingTCPServer(socketserver.ThreadingMixIn, TCPServer):
    pass


max_recv = 32 * 1024


class FilePassthrough:
    def __init__(self, path):
        self.path = path
        self.length = path.stat().st_size

    def __len__(self):
        return self.length


def http_stream_handler(stream, address, server, *, request_handler):
    connection = h11.Connection(our_role=h11.SERVER)

    def send_event(event):
        assert type(event) is not h11.ConnectionClosed
        for data in connection.send_with_data_passthrough(event):
            if isinstance(data, FilePassthrough):
                with data.path.open('rb') as fn:
                    stream.sendfile(fn)
            else:
                stream.sendall(data)

    def read_from_peer():
        if connection.they_are_waiting_for_100_continue:
            send_event(
                h11.InformationalResponse(status_code=100)
            )
        data = stream.recv(max_recv)
        connection.receive_data(data)

    def teardown_peer():
        try:
            stream.shutdown(socket.SHUT_RDWR)
        except:
            pass
        finally:
            stream.close()

    def handle_one_request():
        def event_generator_factory():
            while True:
                event = connection.next_event()
                if event is h11.NEED_DATA:
                    read_from_peer()
                elif type(event) is h11.ConnectionClosed:
                    return
                else:
                    yield event

        event_generator = event_generator_factory()
        sentinel = object()
        event = sentinel
        for event in request_handler(event_generator):
            send_event(event)
        if event is not sentinel and type(event) is not h11.EndOfMessage:
            send_event(h11.EndOfMessage())

        sentinel = object()
        event = next(event_generator, sentinel)
        if event is not sentinel and type(event) is not h11.EndOfMessage:
            print(f"request_handler ignored event {event=}", file=sys.stderr)
            return

    try:
        while True:
            handle_one_request()
            if connection.our_state is h11.MUST_CLOSE:
                teardown_peer()
                return
            else:
                try:
                    connection.start_next_cycle()
                except:
                    return
    except:
        teardown_peer()
        raise
