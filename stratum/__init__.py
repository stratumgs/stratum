import stratum.servers.client
import stratum.servers.web
import tornado.ioloop

def main(client_port=8889, web_port=8888):
    stratum.servers.client.init(client_port)
    stratum.servers.web.init(web_port)
    tornado.ioloop.IOLoop.current().start()
