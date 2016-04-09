import json
import os

import tornado.concurrent
import tornado.ioloop
import tornado.iostream
import tornado.netutil
import tornado.tcpserver


def _make_pipe_pair():
    r1, w1 = os.pipe()
    r2, w2 = os.pipe()
    return (r1, w2), (r2, w1)


class ClientProxy(object):

    def __init__(self, name, stream):
        self.name = name
        self.stream = stream
        self.helper = None
        self.is_available = True

        def stream_closed():
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
        self.connector_server = SingleClientServer()
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


class SingleClientServer(tornado.tcpserver.TCPServer):

    def __init__(self):
        super(SingleClientServer, self).__init__()
        self._stream_future = tornado.concurrent.Future()
        sockets = tornado.netutil.bind_sockets(0, '127.0.0.1')
        self._port = sockets[0].getsockname()[1]
        self.add_sockets(sockets)
        print(sockets)

    def get_port(self):
        return self._port

    def handle_stream(self, stream, address):
        if not self._stream_future.done():
            self._stream_future.set_result(stream)
        self.io_loop.add_callback(lambda: self.stop())

    def get_stream(self):
        return self._stream_future
