import stratum.games.tictactoe


_GAME_ENGINES = {
    "tictactoe": tictactoe
}


def init_game_engine(engine_name, *args):
    return _GAME_ENGINES[engine_name].Engine(*args)


def get_game_configuration(game_name):
    return _GAME_ENGINES[game_name].CONFIG
