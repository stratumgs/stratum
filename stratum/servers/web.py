import datetime
import json
import os
import stratum.games
import stratum.servers.client
import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop


def init(port):
    template_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..", "assets", "templates")
    static_files_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..", "assets", "web")
    app = tornado.web.Application([
        (r"/", MainHandler),
        (r"/games/tictactoe/configure", ConfigureHandler),
        (r"/games/tictactoe/start", StartHandler),
        (r"/games/tictactoe/view/([\d]+)", ViewHandler),
        (r"/games/tictactoe/view/([\d]+)/socket", ViewSocketHandler),
        (r"/assets/(.*)", tornado.web.StaticFileHandler, {"path": static_files_path})
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
        config = stratum.games.get_game_configuration("tictactoe")
        self.render("configure.html", players=players, config=config)


class StartHandler(LoggingHandler):
    def post(self):
        player_ids = self.get_arguments("players")
        game_id = stratum.games.init_game_engine("tictactoe", player_ids=player_ids)
        # self.write("done.")
        self.redirect("/games/tictactoe/view/{}".format(game_id))


class ViewHandler(LoggingHandler):
    def get(self, gid):
        game_template = self.render_string("games/tictactoe.html")
        self.render("view.html", game_template=game_template)


class ViewSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, game_id):
        stratum.games.get_game_runner(int(game_id)).add_view(self)

    def on_message(self, message):
        pass
