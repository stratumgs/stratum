class EngineClient(object):

    def __init__(self, file_descriptors):
        self._read_pipe = open(file_descriptors[0], "r")
        self._write_pipe = open(file_descriptors[1], "wb", buffering=0)

    def write(self, message):
        self._write_pipe.write(message)

    def read(self):
        return self._read_pipe.readline().strip()
