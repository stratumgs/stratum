import tornado.ioloop

import stratumgs.client.server
import stratumgs.config
import stratumgs.web


version = "0.1.1"


def main():
    debug = stratumgs.config.get("global", "debug")
    web_host = stratumgs.config.get("web_server", "host")
    web_port = stratumgs.config.get("web_server", "port")
    client_host = stratumgs.config.get("client_server", "host")
    client_port = stratumgs.config.get("client_server", "port")
    stratumgs.client.server.init(client_host, client_port)
    stratumgs.web.init(web_host, web_port, debug)
    tornado.ioloop.IOLoop.current().start()
