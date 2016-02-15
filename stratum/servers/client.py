import os
import tornado.iostream
import tornado.tcpserver

_CONNECTED_CLIENTS = {}


def init(port):
    client_server = ClientServer()
    client_server.listen(port)


def get_connected_clients():
    return sorted(_CONNECTED_CLIENTS.keys())


def get_connected_client(client_name):
    return _CONNECTED_CLIENTS[client_name]


def _make_pipe_pair():
    r1, w1 = os.pipe()
    r2, w2 = os.pipe()
    return (r1, w2), (r2, w1)


class ClientServer(tornado.tcpserver.TCPServer):

    def handle_stream(self, stream, address):

        def new_client(name):
            name = name.decode().strip()

            client_end, engine_end = _make_pipe_pair()

            _CONNECTED_CLIENTS[name] = engine_end

            to_engine = tornado.iostream.PipeIOStream(client_end[1])
            from_engine = tornado.iostream.PipeIOStream(client_end[0])

            def stream_closed():
                print("client {} died".format(name))
                to_engine.close()
                from_engine.close()

            def message_from_client(msg):
                to_engine.write(msg)
                stream.read_until(b"\n", message_from_client)

            def message_from_engine(msg):
                if msg == b"close\n":
                    stream.close()
                    to_engine.close()
                    from_engine.close()
                    return
                stream.write(msg)
                from_engine.read_until(b"\n", message_from_engine)

            stream.set_close_callback(stream_closed)
            stream.read_until(b"\n", message_from_client)
            from_engine.read_until(b"\n", message_from_engine)

            print("Client {} connected.".format(name))

        stream.read_until(b"\n", new_client)
