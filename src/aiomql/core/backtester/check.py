import socket


class socketserver:
    def __init__(self, address = '192.168.1.15', port = 9090):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = address
        self.port = port
        self.sock.bind((self.address, self.port))
        self.cummdata = ''


    def recvmsg(self):
        g=self.sock.listen(1)
        print(g)
        self.conn, self.addr = self.sock.accept()
        print('connected to', self.addr)
        data = self.conn.recv(10)
        self.cummdata += data.decode("utf-8")


so = socketserver()
so.recvmsg()
