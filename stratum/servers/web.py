import datetime
import os
import stratum.games
import stratum.servers.client
import tornado.web
import tornado.httpserver
import tornado.ioloop


def init(port):
    template_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..",
        "assets",
        "templates")
    app = tornado.web.Application([
        (r"/", MainHandler),
        (r"/game/tictactoe/configure", ConfigureHandler),
        (r"/game/tictactoe/play", PlayHandler)
    ], template_path=template_path, debug=True)
    server = tornado.httpserver.HTTPServer(app)
    server.listen(port)


class LoggingHandler(tornado.web.RequestHandler):
    def prepare(self):
        print("[{datetime}] {req.method} {req.uri} {req.version}".format(
            datetime=datetime.datetime.now().strftime("%m-%d-%Y %H:%M"),
            req=self.request))


class MainHandler(LoggingHandler):
    def get(self):
        self.render("home.html")


class ConfigureHandler(LoggingHandler):
    def get(self):
        players = stratum.servers.client.get_connected_clients()
        self.render("configure.html", players=players)


class PlayHandler(LoggingHandler):
    def post(self):
        player_ids = self.get_arguments("players")
        players = [stratum.servers.client.get_connected_client(pid) for pid in player_ids]
        game_engine = stratum.games.init_game_engine("tictactoe", players)
        game_engine.start()
        self.render("play.html")
