import tornado.concurrent
import tornado.netutil
import tornado.tcpserver


class SingleClientServer(tornado.tcpserver.TCPServer):

    def __init__(self):
        super(SingleClientServer, self).__init__()
        self._stream_future = tornado.concurrent.Future()
        sockets = tornado.netutil.bind_sockets(0, '127.0.0.1')
        self._port = sockets[0].getsockname()[1]
        self.add_sockets(sockets)
        print(sockets)

    def get_port(self):
        return self._port

    def handle_stream(self, stream, address):
        self._stream_future.set_result(stream)
        self.io_loop.add_callback(lambda: self.stop())

    def get_stream(self):
        return self._stream_future
