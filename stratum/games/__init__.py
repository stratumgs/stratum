import stratum.games.tictactoe


_GAME_ENGINES = {
    "tictactoe": tictactoe.Engine
}


def init_game_engine(engine_name, *args):
    return _GAME_ENGINES[engine_name](*args)
