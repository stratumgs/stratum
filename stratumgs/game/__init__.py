"""
.. module stratumgs.game

Contains the functionality to create new games and query information about
existing games.
"""

import stratumgs.game.runner
import stratumgs.client.server

from .games import tictactoe


_GAME_ENGINES = {
    "tictactoe": tictactoe
}

_CREATED_GAME_ID = 0
_CREATED_GAMES = {}


def get_available_game_engines():
    """
        Get a list of the available game engines.

        :returns: A list of tuples of the form ``(game_id, game_configuration)``.
    """

    return [(game_key, get_game_configuration(game_key))
        for game_key in sorted(_GAME_ENGINES.keys())]


def init_game_engine(engine_name, player_ids=[]):
    """
        Initialize a new game engine.

        :param engine_name: The name of the engine to initialize.
        :type engine_name: string
        :param player_ids: A list of the player IDs in the game.
        :type player_ids: list(string)
        :returns: The ID of the newly created game.
    """

    global _CREATED_GAME_ID
    game_id = _CREATED_GAME_ID
    _CREATED_GAME_ID += 1
    players = [stratumgs.client.server.get_connected_client(pid) for pid in player_ids]
    engine_runner = stratumgs.game.runner.init_engine_runner(game_id, _GAME_ENGINES[engine_name].Engine, engine_name, players)
    _CREATED_GAMES[game_id] = engine_runner
    return game_id


def get_game_configuration(game_name):
    """
        Get the configuration for the specified game.

        :param game_name: The name of the game engine to get the configuration for.
        :type game_name: string
        :returns: The game configuration.
    """

    return _GAME_ENGINES[game_name].CONFIG


def get_current_games():
    """
        Get a list of all currently being played games.

        :returns: A list of all current games, in unspecified order.
    """

    return _CREATED_GAMES.items()


def get_game_runner(game_id):
    """
        Get a specific game runner by ID.

        :param game_id: The game ID to retrieve the runner for.
        :type game_id: int
        :returns: The runner.
    """

    return _CREATED_GAMES[game_id]
