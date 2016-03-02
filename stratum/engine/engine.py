from .client import init_engine_client
import json
import sys


class BaseEngine(object):

    def __init__(self, players=[], view_connection=None):
        self.num_players = len(players)
        self._player_clients = [init_engine_client(p) for p in players]
        self._view_client = init_engine_client(view_connection)

    def _send_state(self):
        msg = {
            "type": "message",
            "payload": json.dumps(self.get_state())
        }
        for p in self._player_clients:
            p.write(msg)
        self._view_client.write(msg)

    def run(self):
        self._send_state()
        while not self.is_game_over():
            self.play_turn()
            self._send_state()
        self._send_state()
        for p in self._player_clients:
            p.close()
        self._view_client.close()

    def send_message_to_player(self, player_id, message):
        self._player_clients[player_id].write({
            "type": "message",
            "payload": json.dumps(message)
        })

    def receive_message_from_player(self, player_id):
        obj = self._player_clients[player_id].read()
        if obj["type"] == "close":
            print("Player id {} disconnected.".format(player_id))
            for p in self._player_clients:
                p.close()
            self._view_client.close()
            sys.exit(1)
        return json.loads(obj["payload"])

    def is_game_over(self):
        raise NotImplementedError

    def get_state(self):
        raise NotImplementedError

    def play_turn(self):
        raise NotImplementedError
