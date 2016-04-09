import json

import tornado.ioloop
import tornado.iostream
import tornado.concurrent
import tornado.tcpserver

import stratum.client.proxy

_CONNECTED_CLIENTS = {}


def init(port):
    client_server = ClientProxyServer()
    client_server.listen(port)


def get_connected_client_names():
    return sorted(c.name for c in _CONNECTED_CLIENTS.values() if c.is_available)


def get_connected_client(client_name):
    return _CONNECTED_CLIENTS[client_name]


class StreamProxy(object):

    def __init__(self, stream):
        self._stream = stream
        self._close_callback = None

    def write(self, message):
        self._stream.write(message)

    def read_until(self, delimeter, callback):
        self._stream.read_until(delimeter, callback)

    def set_close_callback(self, callback):
        self._close_callback = callback

    def close(self):
        self._close_callback()


class ClientProxyServer(tornado.tcpserver.TCPServer):

    _NAMELESS_CLIENT_NUMBER = 1

    @classmethod
    def _negotiate_name(cls, name):
        if name is None:
            name = "client-{}".format(cls._NAMELESS_CLIENT_NUMBER)
            cls._NAMELESS_CLIENT_NUMBER += 1
        elif name in _CONNECTED_CLIENTS:
            n = 1
            while True:
                possible_name = "{}-{}".format(name, n)
                if possible_name not in _CONNECTED_CLIENTS:
                    name = possible_name
                    break
        return name

    def handle_stream(self, stream, address):

        def new_client(connect_message):
            connect_message = json.loads(connect_message.decode().strip())

            if connect_message["type"] != "connect":
                print("Invalid message from client {}".format(address))
                return

            name = self._negotiate_name(connect_message["payload"])

            stream.write("{}\n".format(json.dumps({
                "type": "name",
                "payload": name
            })).encode())

            stream_proxy = StreamProxy(stream)

            def stream_closed():
                print("Client {} disconnected.".format(name))
                del _CONNECTED_CLIENTS[name]
                stream_proxy.close()

            stream.set_close_callback(stream_closed)

            _CONNECTED_CLIENTS[name] = stratum.client.proxy.ClientProxy(name, stream_proxy)

            print("Client {} connected.".format(name))

        stream.read_until(b"\n", new_client)
