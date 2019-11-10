from contextlib import contextmanager, ExitStack

import socket
import ssl
import h11


def tls_context():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    return ssl_context


def tls_connect(hostname, port):
    stream = socket.create_connection((hostname, port))
    tls_stream = tls_context().wrap_socket(stream,
                                           server_hostname=hostname)
    return tls_stream


def tls_teardown(stream):
    stream.shutdown(socket.SHUT_RDWR)
    stream.close()


max_recv = 32 * 1024


@contextmanager
def factory(hostname, port):
    with ExitStack() as stack:
        def connect():
            stream = tls_connect(hostname, port)
            stack.callback(lambda: tls_teardown(stream))
            return stream

        def send_events(connection, stream, events):
            for event in events:
                data = connection.send(event)
                stream.sendall(data)

        def collect_events(connection, stream):
            events = []
            while True:
                event = connection.next_event()
                if event is h11.NEED_DATA:
                    data = stream.recv(max_recv)
                    connection.receive_data(data)
                elif type(event) is h11.EndOfMessage:
                    return events
                else:
                    events.append(event)

        stream = connect()
        connection = h11.Connection(our_role=h11.CLIENT)

        def make_request(events):
            nonlocal stream, connection
            if connection.our_state in {h11.MUST_CLOSE, h11.CLOSED}:
                stack.close()
                stream = connect()
                connection = h11.Connection(our_role=h11.CLIENT)
            if connection.states == {h11.CLIENT: h11.DONE, h11.SERVER: h11.DONE}:
                connection.start_next_cycle()

            send_events(connection, stream, events)
            return collect_events(connection, stream)

        yield make_request
