"""
.. module stratumgs.game.runner

Classes and helpers in this module create and manage engine runners, which
manage the game engines which run as background processes.
"""

import json
import multiprocessing
import os

import tornado.ioloop

import tornado.iostream
import stratumgs.client.proxy

import stratumgs.game


def init_engine_runner(game_id, engine, engine_name, players):
    """
        Initialize a new engine runner. Since engine runners can be implemented
        using either pipes or sockets, depending on platform availability, this
        method simplifies creation of new runners.

        :param game_id: The ID of the game being created.
        :type game_id: int
        :param engine: The engine class to initialize in a background process.
        :type engine: ``stratumgs.game.engine.BaseEngine``
        :param engine_name: The name identifier of the engine to initialize.
        :type engine_name: string
        :param players: The players in the game.
        :type players: list(player endpoints)
        :returns: The created engine runner.
    """

    if os.name == "posix":
        return PipeEngineRunner(game_id, engine, engine_name, players)
    else:
        return SocketEngineRunner(game_id, engine, engine_name, players)


def _start_process(engine_constructor, player_endpoints, view_connection):
    """
        The target function for the background process. Intializes and starts
        the specified engine.

        :param engine_constructor: The engine class to initialize.
        :type engine_constructor: ``stratumgs.game.engine.BaseEngine``
        :param player_endpoints: The endpoints of the players in the game.
        :type player_endpoints: list(player endpoints)
        :param view_connection: The endpoints for the view connection.
    """

    engine = engine_constructor(players=player_endpoints, view_connection=view_connection)
    engine.run()


class BaseEngineRunner(object):
    """
        Most of the logic for running a game engine is contained in this class.
        It is extended by classes that implement the communication with the
        view, depending on whether pipes or sockets are in use.

        :param game_id: The ID of the game being created.
        :type game_id: int
        :param engine_constructor: The engine class to initialize in a background process.
        :type engine_constructor: ``stratumgs.game.engine.BaseEngine``
        :param engine_name: The name identifier of the engine to initialize.
        :type engine_name: string
        :param players: The players in the game.
        :type players: list(player endpoints)
    """

    def __init__(self, game_id, engine_constructor, engine_name, players):
        self._last_state = None
        self._connected_views = []

        self.engine_name = engine_name
        self.engine_display_name = stratumgs.game.get_game_configuration(engine_name)["display_name"]
        self.is_running = True
        self.players = players

        view_connection = self.init_view_connection()
 
        player_endpoints = [player.create_endpoints_for_game(game_id) for player in players]
        engine_process = multiprocessing.Process(target=_start_process,
            args=(engine_constructor, player_endpoints, view_connection))
        engine_process.start()

        self.read_from_view_connection(b"\n", self._on_receive_state)

    def _on_receive_state(self, state):
        """
            Callback that is called when a game state is received over the view
            connection.

            :param state: The state that was sent from the engine.
            :type state: A JSON encoded string of the state.
        """

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
        """
            Add a view to the list of connected views.

            :param view: The view to add.
            :type view: :class:``tornado.websocket.WebSocketHandler``
        """

        if self._last_state:
            view.write_message(self._last_state)
        self._connected_views.append(view)


class PipeEngineRunner(BaseEngineRunner):
    """
        An implementation of an engine runner that uses pipes.
    """

    def init_view_connection(self):
        """
            Initializes the view connection using pipes.

            :returns: A tuple containing a ``None`` read endpoint and the write
                      endpoint of the pipe.
        """

        read_pipe, write_pipe = os.pipe()
        self._view_read_pipe = tornado.iostream.PipeIOStream(read_pipe)
        return (None, write_pipe)

    def read_from_view_connection(self, delimiter, callback):
        """
            Read from the view connection.

            :param delimiter: The delimeter to read until.
            :type delimiter: :class:``bytes``
            :param callback: The callback to call when the delimiter is reached.
            :type callbac: function
        """

        self._view_read_pipe.read_until(delimiter, callback)

    def close_view_connection(self):
        """
            Close the relevant connections.
        """

        self._view_read_pipe.close()


class SocketEngineRunner(BaseEngineRunner):
    """
        An implementation of an engine runner that uses sockets.
    """

    def init_view_connection(self):
        """
            Initializes the view connection using pipes.

            :returns: A tuple containing a ``None`` read endpoint and the write
                      endpoint of the pipe.
        """

        self.connector_server = stratumgs.client.proxy.SingleClientServer()
        return self.connector_server.get_port()

    def read_from_view_connection(self, delimiter, callback):
        """
            Read from the view connection.

            :param delimiter: The delimeter to read until.
            :type delimiter: :class:``bytes``
            :param callback: The callback to call when the delimiter is reached.
            :type callbac: function
        """

        tornado.ioloop.IOLoop.current().add_future(
            self.connector_server.get_stream(),
            lambda s: s.result().read_until(delimiter, callback))

    def close_view_connection(self):
        """
            Close the relevant connections.
        """

        tornado.ioloop.IOLoop.current().add_future(
            self.connector_server.get_stream(),
            lambda s: s.result().close())
