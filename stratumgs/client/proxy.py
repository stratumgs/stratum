"""
.. module stratumgs.client.proxy

Proxies clients for the game engines.
"""

import json
import os

import tornado.concurrent
import tornado.ioloop
import tornado.iostream
import tornado.netutil
import tornado.tcpserver

import stratumgs.game


def _make_pipe_pair():
    """
        Make two pipes, and return tuples of the read and write pairs.

        :returns: Read/write pairs for the two pipes.
    """

    r1, w1 = os.pipe()
    r2, w2 = os.pipe()
    return (r1, w2), (r2, w1)


class ClientProxy(object):
    """
        Proxies the raw client stream for the game engine.

        :param name: The client name.
        :type name: string
        :param max_games: The maximum number of simultaneous games the client can support.
        :type max_games: int
        :param stream: The raw client stream.
        :type stream: :class:`tornado.iostream.IOStream`
    """

    def __init__(self, name, supported_games, max_games, stream):
        self.name = name
        self.supported_games = supported_games
        self.max_games = max_games
        self.games_available = max_games
        self.stream = stream
        self.helpers = {}

        self.supported_games_display = []
        for game in supported_games:
            try:
                self.supported_games_display.append(
                    stratumgs.game.get_game_configuration(game)["display_name"])
            except: pass
        self.supported_games_display.sort()

        def stream_closed():
            for helper in self.helpers.values():
                helper.write_to_engine("{}\n".format(json.dumps({
                    "type": "close"
                })).encode())
                helper.close_engine_connection_endpoints()

        def message_from_client(msg):
            obj = json.loads(msg.decode().strip())
            if obj["type"] == "close":
                self.stream.close()
                return
            if obj["game_id"] in self.helpers:
                self.helpers[obj["game_id"]].write_to_engine(msg)
            self.stream.read_until(b"\n", message_from_client)

        self.stream.set_close_callback(stream_closed)
        self.stream.read_until(b"\n", message_from_client)

    def is_available(self):
        """
            Determine whether the client has game slots available.

            :returns: Whether the client has game slots available.
        """

        return self.games_available > 0

    def create_endpoints_for_game(self, game_id):
        """
            Create a set of endpoints to be used by a game engine.

            :param game_id: The id of the game being created.
            :type game_id: int
            :returns: The endpoints for the game engine to use to connect.
        """

        self.games_available -= 1

        if os.name == "posix":
            helper = PipeClientProxyHelper()
        else:
            helper = SocketClientProxyHelper()

        self.helpers[game_id] = helper

        def message_from_engine(msg):
            # decode object and inject game id
            obj = json.loads(msg.decode().strip())
            obj["game_id"] = game_id

            # encode and write object to client
            self.stream.write("{}\n".format(json.dumps(obj)).encode())

            # if engine closing connection, clean up endpoints,
            # make game available, and return
            if obj["type"] == "close":
                helper.close_engine_connection_endpoints()
                del self.helpers[game_id]
                self.games_available += 1
                return

            # read from the engine stream again
            helper.read_from_engine(b"\n", message_from_engine)

        endpoints = helper.init_engine_connection_endpoints()

        helper.read_from_engine(b"\n", message_from_engine)

        self.stream.write("{}\n".format(json.dumps({
            "type": "start",
            "game_id": game_id
        })).encode())

        return endpoints


class PipeClientProxyHelper():
    """
        A helper object to manage connection endpoints. This helpers uses pipes
        to handle communication between the client and engine.
    """

    def init_engine_connection_endpoints(self):
        """
            Initialize the endpoints for the engine.

            :returns: The endpoints.
        """

        client_end, engine_end = _make_pipe_pair()
        self.to_engine = tornado.iostream.PipeIOStream(client_end[1])
        self.from_engine = tornado.iostream.PipeIOStream(client_end[0])
        return engine_end

    def close_engine_connection_endpoints(self):
        """
            Close the endpoints to the engine.
        """

        self.to_engine.close()
        self.from_engine.close()

    def write_to_engine(self, msg):
        """
            Write a message to the engine.

            :param msg: The message to write.
            :type msg: :class:`bytes`
        """

        if not self.to_engine.closed():
            self.to_engine.write(msg)

    def read_from_engine(self, delimeter, callback):
        """
            Read from the engine until the given delimiter is reached. The read
            message will be passed to the callback function.

            :param delimiter: The delimiter to read until.
            :type delimiter: :class:`bytes`
            :param callback: The callback to call.
            :type callback: function
        """

        self.from_engine.read_until(delimeter, callback)


class SocketClientProxyHelper():
    """
        A helper object to manage connection endpoints. This helpers uses 
        sockets to handle communication between the client and engine.
    """

    def init_engine_connection_endpoints(self):
        """
            Initialize the endpoints for the engine.

            :returns: The endpoints.
        """

        self.connector_server = SingleClientServer()
        return self.connector_server.get_port()

    def close_engine_connection_endpoints(self):
        """
            Close the endpoints to the engine.
        """

        tornado.ioloop.IOLoop.current().add_future(
            self.connector_server.get_stream(),
            lambda s: s.result().close())

    def write_to_engine(self, msg):
        """
            Write a message to the engine.

            :param msg: The message to write.
            :type msg: :class:`bytes`
        """

        def cb(s):
            if not s.result().closed():
                s.result().write(msg)
        tornado.ioloop.IOLoop.current().add_future(
            self.connector_server.get_stream(), cb)

    def read_from_engine(self, delimeter, callback):
        """
            Read from the engine until the given delimiter is reached. The read
            message will be passed to the callback function.

            :param delimiter: The delimiter to read until.
            :type delimiter: :class:`bytes`
            :param callback: The callback to call.
            :type callback: function
        """

        tornado.ioloop.IOLoop.current().add_future(
            self.connector_server.get_stream(),
            lambda s: s.result().read_until(delimeter, callback))


class SingleClientServer(tornado.tcpserver.TCPServer):
    """
        A TCP server that runs on an available port, allows a single connection,
        and stores the single connection.
    """

    def __init__(self):
        super(SingleClientServer, self).__init__()
        self._stream_future = tornado.concurrent.Future()
        sockets = tornado.netutil.bind_sockets(0, '127.0.0.1')
        self._port = sockets[0].getsockname()[1]
        self.add_sockets(sockets)
        print(sockets)

    def get_port(self):
        """
            Get the port of the server.

            :returns: The server port.
        """

        return self._port

    def handle_stream(self, stream, address):
        if not self._stream_future.done():
            self._stream_future.set_result(stream)
        self.io_loop.add_callback(lambda: self.stop())

    def get_stream(self):
        """
            Get a future for the stream that connects.

            :returns: A :class:`tornado.concurrent.Future` that will hold the
                      connected stream.
        """

        return self._stream_future
