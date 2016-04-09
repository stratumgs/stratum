import json
import multiprocessing
import os

import tornado.ioloop

import tornado.iostream
import stratum.client.proxy

import stratum.game.games


def init_engine_runner(engine, engine_name, players):
    if os.name == "posix":
        return PipeEngineRunner(engine, engine_name, players)
    else:
        return SocketEngineRunner(engine, engine_name, players)


def _start_process(engine_constructor, player_endpoints, view_connection):
    engine = engine_constructor(players=player_endpoints, view_connection=view_connection)
    engine.run()


class BaseEngineRunner(object):

    def __init__(self, engine_constructor, engine_name, players):
        self._last_state = None
        self._connected_views = []

        self.engine_name = engine_name
        self.engine_display_name = stratum.game.games.get_game_configuration(engine_name)["display_name"]
        self.is_running = True
        self.players = players

        view_connection = self.init_view_connection()
 
        player_endpoints = [player.get_endpoints() for player in players]
        engine_process = multiprocessing.Process(target=_start_process,
            args=(engine_constructor, player_endpoints, view_connection))
        engine_process.start()

        self.read_from_view_connection(b"\n", self._on_receive_state)

    def _on_receive_state(self, state):
        obj = json.loads(state.decode().strip())
        if obj["type"] == "close":
            self.close_view_connection()
            self.is_running = False
            return
        self._last_state = state
        for view in self._connected_views[:]:
            if not view.is_open:
                self._connected_views.remove(view)
                continue
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

    def close_view_connection(self):
        self._view_read_pipe.close()


class SocketEngineRunner(BaseEngineRunner):

    def init_view_connection(self):
        self.connector_server = stratum.client.proxy.SingleClientServer()
        return self.connector_server.get_port()

    def read_from_view_connection(self, delimiter, callback):
        tornado.ioloop.IOLoop.current().add_future(
            self.connector_server.get_stream(),
            lambda s: s.result().read_until(delimiter, callback))

    def close_view_connection(self):
        tornado.ioloop.IOLoop.current().add_future(
            self.connector_server.get_stream(),
            lambda s: s.result().close())
