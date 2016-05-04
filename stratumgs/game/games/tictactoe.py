"""
.. module stratumgs.game.games.tictactoe

A TicTacToe game engine.
"""

from ..engine import BaseEngine

CONFIG = {
    "display_name": "TicTacToe",
    "description": "A game of TicTacToe.",
    "num_players": 2,
    "player_names": ["X", "O"] 
}


def _get_first_if_all_equal(lst):
    """
        Get the first element of a list if all the elements of the list are
        equivalent.

        :param lst: The list of elements.
        :type lst: list
    """

    first = lst[0]
    for el in lst[1:]:
        if el != first:
            return None
    return first


class Engine(BaseEngine):
    """
        The engine class for TicTacToe.

        :param players: The players for the game.
        :type players: list(player endpoints)
        :param view_connection: The view connection endpoints.
    """
    
    def __init__(self, players=[], view_connection=None):
        super(Engine, self).__init__(players=players, view_connection=view_connection)
        self._board = [[None for _ in range(3)] for _ in range(3)]
        self._winner = None
        self._x_turn = True

    def is_game_over(self):
        """
            Check if the game is over. The game is over when a player gets 3 in
            a row, or when all spaces on the board are full.

            :returns: True if the game is over, false otherwise.
        """

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
        """
            Get the current state object for the game. The state of the game
            includes the contents of the board, and the winner of the game.
            Before the game is over or when the outcome is a draw, the winner is
            ``None``.

            :returns: The state.
        """

        return {
            "type": "state",
            "board": self._board,
            "winner": self._winner
        }

    def play_turn(self):
        """
            Play a turn of the game. The current player is prompted to make a
            move. If the move is invalid, the client is asked to repeat the
            turn. Once the client has input a valid move, the move is recorded,
            and the turn ends.
        """

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
