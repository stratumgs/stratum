import multiprocessing
import os
import stratum.util
import tornado.ioloop
import tornado.iostream


def init_engine_runner(engine, players):
    if os.name == "posix":
        return PipeEngineRunner(engine, players)
    else:
        return SocketEngineRunner(engine, players)


class BaseEngineRunner(object):

    def __init__(self, engine_constructor, players):
        self._last_state = None
        self._connected_views = []

        view_connection = self.init_view_connection()

        def start_process():
            engine = engine_constructor(players=players, view_connection=view_connection)
            engine.run()
 
        engine_process = multiprocessing.Process(target=start_process)
        engine_process.start()

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
