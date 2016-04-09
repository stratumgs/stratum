import json
import os
import socket


def init_engine_client(connection_info):
    if os.name == "posix":
        return PipeEngineClient(connection_info)
    else:
        return SocketEngineClient(connection_info)


class PipeEngineClient(object):

    def __init__(self, file_descriptors):
        self._read_pipe = None
        self._write_pipe = None
        if file_descriptors[0] is not None:
            self._read_pipe = open(file_descriptors[0], "rb")
        if file_descriptors[1] is not None:
            self._write_pipe = open(file_descriptors[1], "wb", buffering=0)

    def write(self, message):
        self._write_pipe.write("{}\n".format(json.dumps(message)).encode())

    def read(self):
        return json.loads(self._read_pipe.readline().decode().strip())

    def close(self, write_close=True):
        if write_close:
            self.write({"type": "close"})
        if self._write_pipe:
            self._write_pipe.close()
        if self._read_pipe:
            self._read_pipe.close()


class SocketEngineClient(object):

    def __init__(self, port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self._socket.connect(('127.0.0.1', port))
        self._socket_read_file = self._socket.makefile("rb", 0)
        self._socket_write_file = self._socket.makefile("wb", 0)

    def write(self, message):
        self._socket_write_file.write("{}\n".format(json.dumps(message)).encode())

    def read(self):
        return json.loads(self._socket_read_file.readline().decode().strip())

    def close(self, write_close=True):
        if write_close:
            self.write({"type": "close"})
        self._socket_read_file.close()
        self._socket_write_file.close()
        self._socket.close()
