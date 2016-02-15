import stratum.games.tictactoe


_GAME_ENGINES = {
    "tictactoe": tictactoe.TicTacToeEngine
}


def init_game_engine(engine_name, *args):
    return _GAME_ENGINES[engine_name](*args)
