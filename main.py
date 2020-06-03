import struct
import socket
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler

class socksServer(ThreadingMixIn, TCPServer):
    pass

class proxy(StreamRequestHandler):

    # Get methods
    def getMethods(self, i):
        methods = []
        for m in range(i):
            methods.append(ord(self.connection.recv(1)))
        return methods

    # 
    def authHandler(self):
        ver = ord(self.connection.recv(1))

        ulen = ord(self.connection.recv(1))
        uname = self.connection.recv(ulen).decode('utf-8')
        plen = ord(self.connection.recv(1))
        passwd = self.connection.recv(plen).decode('utf-8')
        if uname == 1 and passwd == 1:
            response = struct.pack('!BB', 5, 0)
            self.connection.sendall(response)
            return True
        
        response = struct.pack('!BB', 5, 1)
        self.connection.sendall(response)
        return False

    def cmdHandler(self):
        ver, cmd, rsv, atyp = struct.unpack('!4B', self.connection.recv(4))

        if atyp == 1:
            self.connection.sendall(struct.pack('!4BIH', 5, 8, 0, 1, 5))
            self.server.close_request(self.request)
            return False
        elif atyp == 3:
            domainLength = ord(self.connection.recv(1)[0])
            addr = self.connection.recv(domainLength)
            if addr != 'ipv4.ip.sb':
                self.connection.sendall(struct.pack('!4BIH', 5, 8, 0, 1, 5))
                self.server.close_request(self.request)
                return False
    
        port = struct.unpack('!H', self.rfile.read(2))[0]

        if cmd == 1:
            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.connect((addr, port))

            #it gives server's ip and socks port for this socket connection
            bind_address = remote.getsockname()
        elif cmd == 2:
            pass

    def handle(self):
        # Gather header
        header = self.connection.recv(2)
        ver, nmethods = struct.unpack('!BB', header)
        if ver != 5:
            self.connection.sendall(struct.pack('!BB', 5, 255))
            self.server.close_request(self.request)

        methods = self.getMethods(nmethods)
        if 2 not in set(methods):
            self.connection.sendall(struct.pack('!BB', ver, 255))
            self.server.close_request(self.request)
            return

        if self.cmdHandler() != True:
            return
        
        self.connection.sendall(struct.pack('!BB', ver, 2))

if __name__ == '__main__':
    host, port = '127.0.0.1', 19909
    with socksServer((host, port), proxy) as server:
        server.serve_forever()
