import os
import socket
import stratum.util
import tornado.ioloop
import tornado.iostream


def init_engine_runner(engine, players):
    if os.name == "posix":
        return PipeEngineRunner(engine, players)
    else:
        return SocketEngineRunner(engine, players)


def init_engine_client(connection_info):
    if os.name == "posix":
        return PipeEngineClient(connection_info)
    else:
        return SocketEngineClient(connection_info)


class BaseEngineRunner(object):

    def __init__(self, engine_constructor, players):
        self._last_state = None
        self._connected_views = []

        view_connection = self.init_view_connection()

        engine = engine_constructor(players=players, view_connection=view_connection)
        engine.start()

        self.read_from_view_connection(b"\n", self._on_receive_state)

    def _on_receive_state(self, state):
        self._last_state = state
        for view in self._connected_views:
            view.write_message(state)
        self.read_from_view_connection(b"\n", self._on_receive_state)

    def add_view(self, view):
        if self._last_state:
            view.write_message(self._last_state)
        self._connected_views.append(view)


class PipeEngineRunner(BaseEngineRunner):

    def init_view_connection(self):
        read_pipe, write_pipe = os.pipe()
        self._view_read_pipe = tornado.iostream.PipeIOStream(read_pipe)
        return (None, write_pipe)

    def read_from_view_connection(self, delimiter, callback):
        self._view_read_pipe.read_until(delimiter, callback)


class SocketEngineRunner(BaseEngineRunner):

    def init_view_connection(self):
        self.connector_server = stratum.util.SingleClientServer()
        return self.connector_server.get_port()

    def read_from_view_connection(self, delimiter, callback):
        tornado.ioloop.IOLoop.current().add_future(
            self.connector_server.get_stream(),
            lambda s: s.result().read_until(delimiter, callback))


class PipeEngineClient(object):

    def __init__(self, file_descriptors):
        self._read_pipe = open(file_descriptors[0], "rb")
        self._write_pipe = open(file_descriptors[1], "wb", buffering=0)

    def write(self, message):
        self._write_pipe.write(message.encode())

    def read(self):
        return self._read_pipe.readline().decode()

    def close(self):
        self.write("close\n")
        self._write_pipe.close()
        self._read_pipe.close()


class SocketEngineClient(object):

    def __init__(self, port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self._socket.connect(('127.0.0.1', port))
        self._socket_read_file = self._socket.makefile("rb", 0)
        self._socket_write_file = self._socket.makefile("wb", 0)

    def write(self, message):
        self._socket_write_file.write(message.encode())

    def read(self):
        return self._socket_read_file.readline().decode()

    def close(self):
        self.write("close\n")
        self._socket_read_file.close()
        self._socket_write_file.close()
        self._socket.close()
