from functools import partial
import socketserver
import socket
import ssl

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
    tls_context.sni_callback = acme_sni_callback
    return tls_context


class TCPServer(socketserver.TCPServer):
    allow_reuse_address = True

    def get_request(self):
        stream, address = self.socket.accept()
        tls_stream = tls_context().wrap_socket(stream, server_side=True)
        return tls_stream, address


class ThreadingTCPServer(socketserver.ThreadingMixIn, TCPServer):
    pass


max_recv = 32 * 1024


def http_stream_handler(stream, address, server, *, request_handler):
    connection = h11.Connection(our_role=h11.SERVER)

    def send_event(event):
        assert type(event) is not h11.ConnectionClosed
        data = connection.send(event)
        stream.sendall(data)

    def read_from_peer():
        if connection.they_are_waiting_for_100_continue:
            send_event(
                h11.InformationalResponse(status_code=100)
            )
        data = stream.recv(max_recv)
        connection.receive_data(data)

    def teardown_peer():
        stream.shutdown(socket.SHUT_RDWR)
        stream.close()

    def handle_one_request():
        events = []

        while True:
            event = connection.next_event()
            if event is h11.NEED_DATA:
                read_from_peer()
            elif type(event) is h11.EndOfMessage:
                for handler_event in request_handler(events):
                    send_event(handler_event)
                return
            elif type(event) is h11.ConnectionClosed:
                return
            else:
                events.append(event)

    try:
        while True:
            handle_one_request()
            if connection.our_state is h11.MUST_CLOSE:
                teardown_peer()
                return
            else:
                connection.start_next_cycle()
    except:
        teardown_peer()
        raise
