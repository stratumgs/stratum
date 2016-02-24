import stratum.engine.runner
import stratum.games.tictactoe
import stratum.servers.client


_GAME_ENGINES = {
    "tictactoe": tictactoe
}

_CREATED_GAME_ID = 0
_CREATED_GAMES = {}


def init_game_engine(engine_name, player_ids=[]):
    global _CREATED_GAME_ID
    game_id = _CREATED_GAME_ID
    _CREATED_GAME_ID += 1
    players = [stratum.servers.client.get_connected_client(pid) for pid in player_ids]
    engine_runner = stratum.engine.runner.init_engine_runner(_GAME_ENGINES[engine_name].Engine, players)
    _CREATED_GAMES[game_id] = engine_runner
    return game_id


def get_game_configuration(game_name):
    return _GAME_ENGINES[game_name].CONFIG


def get_game_runner(game_id):
    return _CREATED_GAMES[game_id]
