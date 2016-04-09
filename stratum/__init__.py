import tornado.ioloop

import stratum.client.client
import stratum.web


def main(client_port=8889, web_port=8888):
    stratum.client.client.init(client_port)
    stratum.web.init(web_port)
    tornado.ioloop.IOLoop.current().start()
