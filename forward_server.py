import socket
import select

if __name__ == '__main__':
    #host, port = '127.0.0.1', 19909
    #with socksServer((host, port), proxy) as server:
    #    server.serve_forever()
    local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_adress = ('127.0.0.1', 19910)
    local.bind(local_adress)
    local.listen(5)

    natTrans = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    natTrans_address = ('127.0.0.1', 19911)
    natTrans.connect(natTrans_address)
    local_in, in_addr = local.accept()

    while True:
        r, w, e = select.select([local_in, natTrans],[],[])
        if local_in in r:
            data = local_in.recv(1024)
            print('remote:', data)
            natTrans.send(data)

        if natTrans in r:
            data = natTrans.recv(1024)
            print('client:', data)
            local_in.sendall(data)
    

