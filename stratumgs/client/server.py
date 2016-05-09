"""
.. module stratumgs.client.server

The client server for stratumgs.
"""

import json

import tornado.ioloop
import tornado.iostream
import tornado.concurrent
import tornado.tcpserver

import stratumgs.client.proxy

_CONNECTED_CLIENTS = {}


def init(port):
    """
        Initialize the client server.

        :param port: The client server port.
        :type port: int
    """

    client_server = ClientProxyServer()
    client_server.listen(port)


def get_available_client_names_for_game(game):
    """
        Get a list of the names of the clients currently connected to the server
        with available game slots.

        :param game: The game that the clients need to support.
        :type game: string
    """

    return sorted(c.name for c in _CONNECTED_CLIENTS.values() if c.is_available() and game in c.supported_games)


def get_connected_clients():
    """
        Get a list of all currently connected clients.
    """

    return sorted(_CONNECTED_CLIENTS.values(), key=lambda c: c.name)


def get_connected_client(client_name):
    """
        Get a connected client by name.

        :param client_name: The name of the client.
        :type client_name: string
    """

    return _CONNECTED_CLIENTS[client_name]


class StreamProxy(object):
    """
        A proxy for :class:`tornado.iostream.IOStream`. It only provides some
        methods of ``IOStream``, as follows: ``write``, ``read_until``,
        ``set_close_callback``, ``close``.

        :param stream: The stream to proxy.
        :type stream: :class:`tornado.iostream.IOStream`
    """

    def __init__(self, stream):
        self._stream = stream
        self._close_callback = None

    def write(self, message):
        self._stream.write(message)

    def read_until(self, delimeter, callback):
        self._stream.read_until(delimeter, callback)

    def set_close_callback(self, callback):
        self._close_callback = callback

    def close(self):
        self._close_callback()


class ClientProxyServer(tornado.tcpserver.TCPServer):
    """
        Listens for new clients and connects them.
    """

    _NAMELESS_CLIENT_NUMBER = 1

    @classmethod
    def _negotiate_name(cls, name):
        """
            Private helper method used to determine a unique client name,
            possibly given a name as a starting point.

            If given name is unique among the currently connected client, then
            this method returns that. If it isn't, appends a number to it to
            make it unique. If the name provided is ``None``, creates a new name
            of the form ``name-#`` where ``#`` is a number that makes the name
            unique.

            :param name: The name.
            :type name: string
            :returns: A unique name for the client.
        """

        if name is None:
            name = "client-{}".format(cls._NAMELESS_CLIENT_NUMBER)
            cls._NAMELESS_CLIENT_NUMBER += 1
        elif name in _CONNECTED_CLIENTS:
            n = 1
            while True:
                possible_name = "{}-{}".format(name, n)
                if possible_name not in _CONNECTED_CLIENTS:
                    name = possible_name
                    break
        return name

    def handle_stream(self, stream, address):

        def new_client(connect_message):
            connect_message = json.loads(connect_message.decode().strip())

            if connect_message["type"] != "connect":
                print("Invalid message type from client {}".format(address))
                return

            name = self._negotiate_name(connect_message["name"])
            try:
                max_games = int(connect_message["max_games"])
            except ValueError:
                print("Invalid max_games parameter from client {}".format(address))
                return
            supported_games = connect_message["supported_games"]

            stream.write("{}\n".format(json.dumps({
                "type": "name",
                "name": name
            })).encode())

            stream_proxy = StreamProxy(stream)

            def stream_closed():
                print("Client {} disconnected.".format(name))
                del _CONNECTED_CLIENTS[name]
                stream_proxy.close()

            stream.set_close_callback(stream_closed)

            _CONNECTED_CLIENTS[name] = stratumgs.client.proxy.ClientProxy(name, supported_games, max_games, stream_proxy)

            print("Client {} connected.".format(name))

        stream.read_until(b"\n", new_client)
