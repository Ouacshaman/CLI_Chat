import socket
import threading


class Server:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen()
        print(f'Server started on {host}:{port}, waiting for connections...')

    def accept(self, convo):
        while True:
            conn, addr = self.sock.accept()
            print(f'Connected by {addr}')
            threading.Thread(target=self.handle_client,
                             args=(conn, convo)).start()

    def handle_client(self, conn, convo):
        with conn:
            while True:
                data = conn.recv(8096)
                if not data:
                    break
                convo.append(data.decode('utf-8'))
                conn.sendall(data)

    def close(self):
        self.sock.close()


convo = []
s = Server("127.0.0.1", 8080)

try:
    s.accept(convo)
except KeyboardInterrupt:
    print("Server Ended")
    s.close()


for item in convo:
    print(item)
