import os
import stratum.util
import tornado.ioloop
import tornado.iostream
import tornado.concurrent
import tornado.tcpserver

_CONNECTED_CLIENTS = {}


def init(port):
    client_server = ClientProxyServer()
    client_server.listen(port)


def get_connected_clients():
    return sorted(_CONNECTED_CLIENTS.keys())


def get_connected_client(client_name):
    return _CONNECTED_CLIENTS[client_name]


def _make_pipe_pair():
    r1, w1 = os.pipe()
    r2, w2 = os.pipe()
    return (r1, w2), (r2, w1)


class ClientProxyServer(tornado.tcpserver.TCPServer):

    def handle_stream(self, stream, address):

        def new_client(name):
            name = name.decode().strip()

            if os.name == "posix":
                helper = PipeClientProxyServerHelper()
            else:
                helper = SocketClientProxyServerHelper()

            _CONNECTED_CLIENTS[name] = helper.init_engine_connection_endpoints()

            def stream_closed():
                print("client {} died".format(name))
                helper.close_engine_connection_endpoints()

            def message_from_client(msg):
                helper.write_to_engine(msg)
                stream.read_until(b"\n", message_from_client)

            def message_from_engine(msg):
                if msg == b"close\n":
                    stream.close()
                    helper.close_engine_connection_endpoints()
                    return
                stream.write(msg)
                helper.read_from_engine(b"\n", message_from_engine)

            stream.set_close_callback(stream_closed)
            stream.read_until(b"\n", message_from_client)
            helper.read_from_engine(b"\n", message_from_engine)

            print("Client {} connected.".format(name))

        stream.read_until(b"\n", new_client)


class PipeClientProxyServerHelper():

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


class SocketClientProxyServerHelper():

    def init_engine_connection_endpoints(self):
        self.connector_server = stratum.util.SingleClientServer()
        return self.connector_server.get_port()

    def close_engine_connection_endpoints(self):
        tornado.ioloop.IOLoop.current().add_future(
            self.connector_server.get_stream(),
            lambda s: s.result().close())

    def write_to_engine(self, msg):
        tornado.ioloop.IOLoop.current().add_future(
            self.connector_server.get_stream(),
            lambda s: s.result().write(msg))

    def read_from_engine(self, delimeter, callback):
        tornado.ioloop.IOLoop.current().add_future(
            self.connector_server.get_stream(),
            lambda s: s.result().read_until(delimeter, callback))
