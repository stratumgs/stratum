import stratum.engine


CONFIG = {
    "num_players": 2,
    "player_names": ["X", "O"] 
}


def _get_first_if_all_equal(lst):
    first = lst[0]
    for el in lst[1:]:
        if el != first:
            return None
    return first


class Engine(stratum.engine.BaseEngine):
    
    def __init__(self, players=[], view_connection=None):
        super(Engine, self).__init__(players=players, view_connection=view_connection)
        self._board = [[None for _ in range(3)] for _ in range(3)]
        self._winner = None
        self._x_turn = True

    def is_game_over(self):
        for i in range(3):
            row_val = _get_first_if_all_equal(self._board[i])
            col_val = _get_first_if_all_equal(tuple(self._board[j][i] for j in range(3)))
            if row_val == "X" or col_val == "X":
                self._winner = "X"
                return True
            elif row_val == "O" or col_val == "O":
                self._winner = "O"
                return True
        diag1_val = _get_first_if_all_equal(tuple(self._board[i][i] for i in range(3)))
        diag2_val = _get_first_if_all_equal(tuple(self._board[2-i][i] for i in range(3)))
        if diag1_val == "X" or diag2_val == "X":
            self._winner = "X"
            return True
        elif diag1_val == "O" or diag2_val == "O":
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
        while True:
            move = self.receive_message_from_player(cur_player_id)
            row, col = move["row"], move["column"]
            error = None
            if row > 2 or col > 2:
                error = "out-of-bounds"
            elif self._board[row][col] is not None:
                error = "space-not-empty"
            if error is None:
                break
            self.send_message_to_player(cur_player_id, {
                "type": "repeat-turn",
                "error": error,
                "last-move": move
            })
        self._board[move["row"]][move["column"]] = cur_player_letter
        self._x_turn = not self._x_turn
