import stratum.servers.client
import stratum.servers.web
import tornado.ioloop

if __name__ == "__main__":
    stratum.servers.client.init(8889)
    stratum.servers.web.init(8888)
    tornado.ioloop.IOLoop.current().start()
