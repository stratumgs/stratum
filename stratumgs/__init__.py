import tornado.ioloop

import stratumgs.client.server
import stratumgs.web


def main(client_port=8889, web_port=8888):
    stratumgs.client.server.init(client_port)
    stratumgs.web.init(web_port)
    tornado.ioloop.IOLoop.current().start()
