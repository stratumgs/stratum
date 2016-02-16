import json
import multiprocessing
import os
import stratum.engine
import tornado.ioloop


CONFIG = {
    "num_players": 2,
    "player_names": ["X", "O"] 
}


class Engine(multiprocessing.Process):
    
    def __init__(self, players=[], view_pipe_fd=None):
        super(Engine, self).__init__()
        print(tornado.ioloop.IOLoop.instance())
        self._board = [[None for _ in range(3)] for _ in range(3)]
        self._winner = None
        self._x_turn = True
        self._x_client = stratum.engine.EngineClient(players[0])
        self._o_client = stratum.engine.EngineClient(players[1])
        self._view_pipe = open(view_pipe_fd, "wb", buffering=0)

    def _is_game_over(self):
        for row in self._board:
            if all("x" == cell for cell in row):
                self._winner = "x"
                return True
            elif all("o" == cell for cell in row):
                self._winner = "o"
                return True
        for col in range(3):
            col = tuple(self._board[i][col] for i in range(3))
            if all("x" == cell for cell in col):
                self._winner = "x"
                return True
            elif all("o" == cell for cell in col):
                self._winner = "o"
                return True
        for mod in (1, -1):
            diag = tuple(self._board[mod*i][i] for i in range(3))
            if all("x" == cell for cell in diag):
                self._winner = "x"
                return True
            elif all("o" == cell for cell in diag):
                self._winner = "o"
                return True
        return not any(None == cell for row in self._board for cell in row)

    def _get_player_move(self):
        player = None
        move = None
        if self._x_turn:
            player = "x"
            self._x_client.write(b"turn\n")
            move = self._x_client.read()
        else:
            player = "o"
            self._o_client.write(b"turn\n")
            move = self._o_client.read()
        self._x_turn = not self._x_turn
        (row, col) = (int(x) for x in move.split(","))
        self._board[row][col] = player

    def _send_state(self):
        state = "state {}\n".format(json.dumps(self._board)).encode()
        self._x_client.write(state)
        self._o_client.write(state)
        self._view_pipe.write(state)

    def run(self):
        while not self._is_game_over():
            print()
            for row in self._board:
                print(row)
            print()
            self._send_state()
            self._get_player_move()
        self._send_state()
        print("Player {} wins".format(self._winner))
        self._o_client.close()
        self._x_client.close()
        self._view_pipe.close()
