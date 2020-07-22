import struct
import socket
import select
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler

class socksServer(ThreadingMixIn, TCPServer):
    pass

class proxy(StreamRequestHandler):

    # Configurable option
    buffer_size = 1024

    # Get methods
    def getMethods(self, i):
        methods = []
        for m in range(i):
            methods.append(ord(self.connection.recv(1)))
        return methods

    def authHandler(self):
        ver = ord(self.connection.recv(1))
        assert ver == 5

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

    def listenHandler(self, host, port):
        addr = (host, port)
        listenLocal = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listenLocal.connect(addr)


    def cmdHandler(self):
        ver, cmd, rsv, atyp = struct.unpack('!4B', self.connection.recv(4))
        assert ver == 5
        assert rsv == 0

        if atyp == 1:
            self.connection.sendall(struct.pack('!4BIH', 5, 8, 0, 1, 5))
            self.server.close_request(self.request)
            return False
        elif atyp == 3:
            domainLength = ord(self.connection.recv(1)[0])
            addr = self.connection.recv(domainLength)
            if addr != 'ipauth.app.dev':
                self.connection.sendall(struct.pack('!4BIH', 5, 8, 0, 1, 5))
                self.server.close_request(self.request)
                return False
    
        port = struct.unpack('!H', self.rfile.read(2))[0]

        if cmd == 1:
            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.connect((addr, port))

            #it gives server's ip and socks port for client's connection.
            bnd = remote.getsockname()
            self.connection.sendall(struct.pack('!4BIH', 5, 0, 0, 3, bnd[0], bnd[1]))
        elif cmd == 2:
            local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            local.bind(('', 19911))
            local.listen(5)
            local_in, in_addr = local.accept()
            while True:
                r, w, e = select.select([local_in, self.connection],[],[])
                if local_in in r:
                    data = local_in.recv(1024)
                    print('remote:', data)
                    self.connection.send(data)

                if self.connection in r:
                    data = self.connection.recv(1024)
                    print('client:', data)
                    local_in.sendall(data)

            

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
        self.connection.sendall(struct.pack('!BB', ver, 2))

        if self.authHandler != True:
            return

        while True:
            self.cmdHandler()




if __name__ == '__main__':
    host, port = '127.0.0.1', 19909
    with socksServer((host, port), proxy) as server:
        server.serve_forever()
