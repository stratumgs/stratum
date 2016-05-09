"""
.. module stratumgs.web

The web server for stratumgs.
"""

import datetime
import os

import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop

import stratumgs.game
import stratumgs.client.server


def init(port):
    """
        Initialize the web server.

        :param port: The web server port.
        :type port: int
   """

    template_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "assets", "templates")
    static_files_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "assets", "web")
    app = tornado.web.Application([
        tornado.web.url(r"/", HomeHandler, name="main"),
        tornado.web.url(r"/games", GamesHandler, name="games"),
        tornado.web.url(r"/games/([^/]+)/configure", ConfigureHandler, name="configure"),
        tornado.web.url(r"/games/([^/]+)/start", StartHandler, name="start"),
        tornado.web.url(r"/games/([^/]+)/view/([\d]+)", ViewHandler, name="view"),
        tornado.web.url(r"/games/([^/]+)/view/([\d]+)/socket", ViewSocketHandler, name="view_socket"),
        tornado.web.url(r"/matches", MatchesHandler, name="matches"),
        tornado.web.url(r"/players", PlayersHandler, name="players"),
        tornado.web.url(r"/assets/(.*)", tornado.web.StaticFileHandler, {"path": static_files_path}, name="static")
    ], template_path=template_path, debug=True)
    server = tornado.httpserver.HTTPServer(app)
    server.listen(port)


class LoggingHandler(tornado.web.RequestHandler):
    """
        Base class for all request handlers. Logs the time, method, uri, and
        HTTP version to the console for each request.
    """

    def prepare(self):
        print("[{datetime}] {req.method} {req.uri} {req.version}".format(
            datetime=datetime.datetime.now().strftime("%m-%d-%Y %H:%M"),
            req=self.request))


class HomeHandler(LoggingHandler):
    """
        Renders the home page.
    """

    def get(self):
        self.render("home.html")


class GamesHandler(LoggingHandler):
    """
        Lists the available games to play.
    """

    def get(self):
        games = stratumgs.game.get_available_game_engines()
        self.render("games.html", games=games)


class ConfigureHandler(LoggingHandler):
    """
        Displays a configuration screen to configure a new game.
    """

    def get(self, game):
        players = stratumgs.client.server.get_available_client_names_for_game(game)
        config = stratumgs.game.get_game_configuration(game)
        self.render("configure.html", players=players, game_name=game, config=config)


class StartHandler(LoggingHandler):
    """
        Starts a new game.
    """

    def post(self, game):
        player_ids = self.get_arguments("players")
        game_id = stratumgs.game.init_game_engine(game, player_ids=player_ids)
        self.redirect("/games/tictactoe/view/{}".format(game_id))


class ViewHandler(LoggingHandler):
    """
        Displays a game.
    """

    def get(self, game, gid):
        game_template = self.render_string("games/{}.html".format(game))
        self.render("view.html", game_name=game, game_template=game_template)


class ViewSocketHandler(tornado.websocket.WebSocketHandler):
    """
        Handles websocket connections for viewing games.
    """

    def open(self, game, game_id):
        self.is_open = True
        stratumgs.game.get_game_runner(int(game_id)).add_view(self)

    def on_close(self):
        self.is_open = False

    def on_message(self, message):
        pass


class MatchesHandler(LoggingHandler):
    """
        Displays current matches.
    """

    def get(self):
        all_matches = stratumgs.game.get_current_games()
        active_matches = []
        inactive_matches = []
        for match in all_matches:
            if match[1].is_running:
                active_matches.append(match)
            else:
                inactive_matches.append(match)
        self.render("matches.html",
            active_matches=active_matches, inactive_matches=inactive_matches)


class PlayersHandler(LoggingHandler):
    """
        List currently connected players.
    """

    def get(self):
        players = stratumgs.client.server.get_connected_clients()
        self.render("players.html", players=players)
