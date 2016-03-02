import stratum.engine


CONFIG = {
    "num_players": 2,
    "player_names": ["X", "O"] 
}


class Engine(stratum.engine.BaseEngine):
    
    def __init__(self, players=[], view_connection=None):
        super(Engine, self).__init__(players=players, view_connection=view_connection)
        self._board = [[None for _ in range(3)] for _ in range(3)]
        self._winner = None
        self._x_turn = True

    def is_game_over(self):
        for row in self._board:
            if all("X" == cell for cell in row):
                self._winner = "X"
                return True
            elif all("O" == cell for cell in row):
                self._winner = "O"
                return True
        for col in range(3):
            col = tuple(self._board[i][col] for i in range(3))
            if all("X" == cell for cell in col):
                self._winner = "X"
                return True
            elif all("O" == cell for cell in col):
                self._winner = "O"
                return True
        for mod in (1, -1):
            diag = tuple(self._board[mod*i][i] for i in range(3))
            if all("X" == cell for cell in diag):
                self._winner = "X"
                return True
            elif all("O" == cell for cell in diag):
                self._winner = "O"
                return True
        return not any(None == cell for row in self._board for cell in row)

    def get_state(self):
        return {
            "type": "state",
            "board": self._board,
            "winner": self._winner
        }

    def play_turn(self):
        cur_player_id, cur_player_letter = (0, "X") if self._x_turn else (1, "O")
        self.send_message_to_player(cur_player_id, {"type": "turn"})
        move = self.receive_message_from_player(cur_player_id)
        self._board[move["row"]][move["column"]] = cur_player_letter
        self._x_turn = not self._x_turn
