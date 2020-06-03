import struct
import socket

def packMessage():
    message = struct.pack('!3B', 5, 1, 2)
    return message

def credits():
    uname = 'admin'
    passwd = 'admin'
    message = struct.pack('!BBpBp', 5, len(uname), uname, len(passwd), passwd)
    return message

def requestClient():
    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socksServer = ('127.0.0.1', 19909)
    socks.connect(socksServer)
    socks.sendall(packMessage())
    header = socks.recv(2)
    ver, method = struct.unpack('!BB', header)
    print(socks.recv(2))
    if ver != 5 and method != 2:
        socks.close()
        return 'bad response!'
    
    socks.send(credits())
    socks.close()

if __name__ == '__main__':
    requestClient()
