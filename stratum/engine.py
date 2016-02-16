import os
import tornado.iostream


class EngineRunner(object):

    def __init__(self, engine, players):
        self._last_state = None
        self._connected_views = []

        read_pipe, write_pipe = os.pipe()
        self._read_pipe = tornado.iostream.PipeIOStream(read_pipe)

        self._engine = engine(players=players, view_pipe_fd=write_pipe)
        self._engine.start()

        self._read_pipe.read_until(b"\n", self._on_receive_state)

    def _on_receive_state(self, state):
        self._last_state = state
        for view in self._connected_views:
            view.write_message(state)
        self._read_pipe.read_until(b"\n", self._on_receive_state)

    def add_view(self, view):
        if self._last_state:
            view.write_message(self._last_state)
        self._connected_views.append(view)


class EngineClient(object):

    def __init__(self, file_descriptors):
        self._read_pipe = open(file_descriptors[0], "r")
        self._write_pipe = open(file_descriptors[1], "wb", buffering=0)

    def write(self, message):
        self._write_pipe.write(message)

    def read(self):
        return self._read_pipe.readline().strip()

    def close(self):
        self.write(b"close\n")
        self._write_pipe.close()
        self._read_pipe.close()
