import socket
from tornado.tcpserver import TCPServer

class OnlyOnceException(BaseException):
    pass

class OnlyOnce(object):
    def __init__(self):
        self.tcp_server = TCPServer()
        try:
            self.tcp_server.listen(44556)
        except socket.error as e:
            raise OnlyOnceException()

    def __del__(self):
        if self.tcp_server is not None:
            self.tcp_server.stop()
