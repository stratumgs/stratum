from .client import init_engine_client
import json


class BaseEngine(object):

    def __init__(self, players=[], view_connection=None):
        self.num_players = len(players)
        self._player_clients = [init_engine_client(p) for p in players]
        self._view_client = init_engine_client(view_connection)

    def _send_state(self):
        state = json.dumps(self.get_state()) + "\n"
        for p in self._player_clients:
            p.write(state)
        self._view_client.write(state)

    def run(self):
        self._send_state()
        while not self.is_game_over():
            self.play_turn()
            self._send_state()
        for p in self._player_clients:
            p.close()
        self._view_client.close(False)

    def send_message_to_player(self, player_id, message):
        message = json.dumps(message) + "\n"
        self._player_clients[player_id].write(message)

    def receive_message_from_player(self, player_id):
        return json.loads(self._player_clients[player_id].read().strip())

    def is_game_over(self):
        raise NotImplementedError

    def get_state(self):
        raise NotImplementedError

    def play_turn(self):
        raise NotImplementedError
