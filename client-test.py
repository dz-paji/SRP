import socket

if __name__ == "__main__":
    remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_address = ('127.0.0.1', 19910)
    remote.connect(remote_address)

    while True:
        userInput = input()
        for i in range(0, 10):
            remote.sendall(b'i')