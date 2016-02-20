import os
import stratum.util
import tornado.gen
import tornado.ioloop
import tornado.iostream
import tornado.concurrent
import tornado.tcpserver

_CONNECTED_CLIENTS = {}


def init(port):
    if os.name == "posix":
        client_server = PipeClientProxyServer()
    else:
        client_server = SocketClientProxyServer()
    client_server.listen(port)


def get_connected_clients():
    return sorted(_CONNECTED_CLIENTS.keys())


def get_connected_client(client_name):
    return _CONNECTED_CLIENTS[client_name]


def _make_pipe_pair():
    r1, w1 = os.pipe()
    r2, w2 = os.pipe()
    return (r1, w2), (r2, w1)


class BaseClientProxyServer(tornado.tcpserver.TCPServer):

    @tornado.gen.coroutine
    def handle_stream(self, stream, address):

        def new_client(name):
            name = name.decode().strip()

            _CONNECTED_CLIENTS[name] = self.init_engine_connection_endpoints()

            def stream_closed():
                print("client {} died".format(name))
                self.close_engine_connection_endpoints()

            def message_from_client(msg):
                self.write_to_engine(msg)
                stream.read_until(b"\n", message_from_client)

            def message_from_engine(msg):
                if msg == b"close\n":
                    stream.close()
                    self.close_engine_endpoints()
                    return
                stream.write(msg)
                self.read_from_engine(b"\n", message_from_engine)

            stream.set_close_callback(stream_closed)
            stream.read_until(b"\n", message_from_client)
            self.read_from_engine(b"\n", message_from_engine)

            print("Client {} connected.".format(name))

        stream.read_until(b"\n", new_client)


class PipeClientProxyServer(BaseClientProxyServer):

    def init_engine_connection_endpoints(self, name):
        client_end, engine_end = _make_pipe_pair()
        self.to_engine = tornado.iostream.PipeIOStream(client_end[1])
        self.from_engine = tornado.iostream.PipeIOStream(client_end[0])
        return engine_end

    def close_engine_connection_endpoints(self):
        self.to_engine.close()
        self.from_engine.close()

    def write_to_engine(msg):
        self.to_engine.write(msg)

    def read_from_engine(delimeter, callback):
        self.from_engine.read_until(delimeter, callback)


class SocketClientProxyServer(BaseClientProxyServer):

    def init_engine_connection_endpoints(self):
        self.connector_server = stratum.util.SingleClientServer()
        return self.connector_server.get_port()

    @tornado.gen.coroutine
    def close_engine_connection_endpoints(self):
        stream = yield self.connector_server.get_stream()
        stream.close()

    @tornado.gen.coroutine
    def write_to_engine(self, msg):
        stream = yield self.connector_server.get_stream()
        stream.write(msg)

    @tornado.gen.coroutine
    def read_from_engine(self, delimeter, callback):
        stream = yield self.connector_server.get_stream()
        stream.read_until(delimeter, callback)
