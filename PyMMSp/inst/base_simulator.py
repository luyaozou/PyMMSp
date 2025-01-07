#! encoding = utf-8

""" BaseSimDecoder class
Take out this class to avoid circular import
because each instrument module imports the BaseSimDecoder class
and then the base.py module imports all instrument modules
"""


class BaseSimDecoder:
    """ Basic simulator decoder class
    It provides an internal buffer to stack any code sent to the simulator,
    and pop the buffer on query request.
    Other specific instrument simulators can inherit this parent class
    and override the decoding method.
    """

    def __init__(self):
        self._buffer = []
        self._buffer_byte = bytearray()

    def str_in(self, code):
        """ Send code to simulator """
        self._buffer.append(code)

    def str_out(self):
        return self._buffer.pop()

    def byte_in(self, byte):
        """ Send byte to simulator """
        self._buffer_byte.extend(byte)

    def byte_out(self, byte, skip=0):
        """ Pop byte from simulator """
        data = self._buffer_byte[skip:byte + skip]
        self._buffer_byte = self._buffer_byte[byte + skip:]
        return data

    def interpret(self, code):
        """ Decode the code """
        pass


class SimHandle:
    """ Instrument simulator handle """

    def __init__(self, *args, **kwargs):
        """ ignore args and kwargs passed to real instrument handle """
        self._stat = True
        self._decoder = BaseSimDecoder()

    def send(self, code):
        """ Interpret the code and send the result to internal buffer """
        self._decoder.interpret(code)

    def recv(self, byte=64, skip=0):
        """ To make life easier, read directly the buffer string instead of bytes """
        return self._decoder.str_out()

    def query(self, code, byte=64, skip=0):
        """ Interpret the code and send the result to internal buffer """
        self.send(code)
        return self.recv(byte, skip)

    def close(self):
        self._stat = False

    def open(self):
        self._stat = True

    @property
    def is_sim(self):
        return True

    @property
    def is_active(self):
        return self._stat

    def set_decoder(self, decoder):
        self._decoder = decoder
