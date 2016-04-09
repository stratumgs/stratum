import json
import os

import tornado.ioloop
import tornado.iostream
import tornado.concurrent
import tornado.tcpserver

import stratum.client.util

_CONNECTED_CLIENTS = {}

_NAMELESS_CLIENT_NUMBER = 1


def init(port):
    client_server = ClientProxyServer()
    client_server.listen(port)


def get_connected_client_names():
    return sorted(c.name for c in _CONNECTED_CLIENTS.values() if c.is_available)


def get_connected_client(client_name):
    return _CONNECTED_CLIENTS[client_name]


def _make_pipe_pair():
    r1, w1 = os.pipe()
    r2, w2 = os.pipe()
    return (r1, w2), (r2, w1)


class ClientProxy(object):

    def __init__(self, stream, address):

        self.stream = stream
        self.helper = None
        self.is_available = True

        def new_client(connect_message):
            connect_message = json.loads(connect_message.decode().strip())

            if connect_message["type"] != "connect":
                print("Invalid message from client {}".format(address))
                return

            self.set_name(connect_message["payload"])

            stream.write("{}\n".format(json.dumps({
                "type": "name",
                "payload": self.name
            })).encode())

            _CONNECTED_CLIENTS[self.name] = self

            print("Client {} connected.".format(self.name))

        def stream_closed():
            print("client {} died".format(self.name))
            del _CONNECTED_CLIENTS[self.name]
            if self.helper:
                self.helper.write_to_engine("{}\n".format(json.dumps({
                    "type": "close"
                })).encode())
                self.helper.close_engine_connection_endpoints()

        def message_from_client(msg):
            if self.helper:
                self.helper.write_to_engine(msg)
                obj = json.loads(msg.decode().strip())
                if obj["type"] == "close":
                    self.stream.close()
                    self.helper.close_engine_connection_endpoints()
                    return
            self.stream.read_until(b"\n", message_from_client)

        stream.read_until(b"\n", new_client)
        self.stream.set_close_callback(stream_closed)
        self.stream.read_until(b"\n", message_from_client)


    def get_endpoints(self):
        self.is_available = False

        if os.name == "posix":
            self.helper = PipeClientProxyHelper()
        else:
            self.helper = SocketClientProxyHelper()

        def message_from_engine(msg):
            self.stream.write(msg)
            obj = json.loads(msg.decode().strip())
            if obj["type"] == "close":
                self.stream.close()
                self.helper.close_engine_connection_endpoints()
                return
            self.helper.read_from_engine(b"\n", message_from_engine)

        endpoints = self.helper.init_engine_connection_endpoints()

        self.helper.read_from_engine(b"\n", message_from_engine)

        return endpoints


    def set_name(self, name):
        if name is None:
            global _NAMELESS_CLIENT_NUMBER
            name = "client-{}".format(_NAMELESS_CLIENT_NUMBER)
            _NAMELESS_CLIENT_NUMBER += 1
        elif name in _CONNECTED_CLIENTS:
            n = 1
            while True:
                possible_name = "{}-{}".format(name, n)
                if possible_name not in _CONNECTED_CLIENTS:
                    name = possible_name
                    break
        self.name = name



class ClientProxyServer(tornado.tcpserver.TCPServer):

    def handle_stream(self, stream, address):
        ClientProxy(stream, address)


class PipeClientProxyHelper():

    def init_engine_connection_endpoints(self):
        client_end, engine_end = _make_pipe_pair()
        self.to_engine = tornado.iostream.PipeIOStream(client_end[1])
        self.from_engine = tornado.iostream.PipeIOStream(client_end[0])
        return engine_end

    def close_engine_connection_endpoints(self):
        self.to_engine.close()
        self.from_engine.close()

    def write_to_engine(self, msg):
        if not self.to_engine.closed():
            self.to_engine.write(msg)

    def read_from_engine(self, delimeter, callback):
        self.from_engine.read_until(delimeter, callback)


class SocketClientProxyHelper():

    def init_engine_connection_endpoints(self):
        self.connector_server = stratum.client.util.SingleClientServer()
        return self.connector_server.get_port()

    def close_engine_connection_endpoints(self):
        tornado.ioloop.IOLoop.current().add_future(
            self.connector_server.get_stream(),
            lambda s: s.result().close())

    def write_to_engine(self, msg):
        def cb(s):
            if not s.result().closed():
                s.result().write(msg)
        tornado.ioloop.IOLoop.current().add_future(
            self.connector_server.get_stream(), cb)

    def read_from_engine(self, delimeter, callback):
        tornado.ioloop.IOLoop.current().add_future(
            self.connector_server.get_stream(),
            lambda s: s.result().read_until(delimeter, callback))
