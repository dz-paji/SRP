import socket

class simple_server():
    buffer_size = 1024
    def session_handler(self, newSession):
        newSession.send(b'what?')
        reply = ''
        while len(reply) == 0:
            data = newSession.recv(self.buffer_size).decode()
            if data == 'h':
                reply = 'yes! yes! fuck you, too!'
            if data == 's':
                reply = 'put it in, baby'
            else:
                reply = ''
            print(data)
            print(reply)
        newSession.send(bytes(reply, 'UTF-8'))
        newSession.close()
        
    def server_start(self, listen_addr):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(listen_addr)
        server.listen(5)
        in_traffic, in_addr = server.accept()
        print('new connection from:', in_addr)
        self.session_handler(self, in_traffic)

if __name__ == '__main__':
    simple_server.server_start(simple_server, ('', 19911))