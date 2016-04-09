import tornado.ioloop

import stratum.client.server
import stratum.web


def main(client_port=8889, web_port=8888):
    stratum.client.server.init(client_port)
    stratum.web.init(web_port)
    tornado.ioloop.IOLoop.current().start()
