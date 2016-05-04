import json
import sys

from .client import init_engine_client


class BaseEngine(object):
    """
        Contains the base code for all game engines. Engines must extend this
        class, and need to implement ``is_game_over``, ``get_state``, and
        ``play_turn``.

        :param players: The list of player endpoints.
        :type players: list(player endpoints)
        :param view_connection: The view connection endpoints.
    """

    def __init__(self, players=[], view_connection=None):
        self.num_players = len(players)
        self._player_clients = [init_engine_client(p) for p in players]
        self._view_client = init_engine_client(view_connection)

    def _send_state(self):
        """
            Send the current state of the game to the view client.
        """

        msg = {
            "type": "message",
            "payload": json.dumps(self.get_state())
        }
        for p in self._player_clients:
            p.write(msg)
        self._view_client.write(msg)

    def run(self):
        """
            Start the main game loop.
        """

        self._send_state()
        while not self.is_game_over():
            self.play_turn()
            self._send_state()
        self._send_state()
        for p in self._player_clients:
            p.close()
        self._view_client.close()

    def send_message_to_player(self, player_id, message):
        """
            Send the given message to the given player ID. The message gets
            encoded and sent to the client.

            :param player_id: The ID of the player to send a message to.
            :type player_id: int
            :param message: The message to send.
            :type message: string
        """

        self._player_clients[player_id].write({
            "type": "message",
            "payload": json.dumps(message)
        })

    def receive_message_from_player(self, player_id):
        """
            A method that blocks until a message is received from the given
            player.

            :param player_id: The ID of the player to receive a message from.
            :type player_id: int
            :returns: The message received from the player.
        """

        obj = self._player_clients[player_id].read()
        if obj["type"] == "close":
            print("Player id {} disconnected.".format(player_id))
            for p in self._player_clients:
                p.close()
            self._view_client.close()
            sys.exit(1)
        return json.loads(obj["payload"])

    def is_game_over(self):
        """
            Must be implemented by the game engine. Checks if the game is over.

            :returns: Tue if the game is over, false otherwise.
        """

        raise NotImplementedError

    def get_state(self):
        """
            Must be implemented by the game engine. Get the current state of the
            game.

            :returns: The state of the game.
        """

        raise NotImplementedError

    def play_turn(self):
        """
            Must be implemented by the game engine. Plays a turn of the game.
        """

        raise NotImplementedError
