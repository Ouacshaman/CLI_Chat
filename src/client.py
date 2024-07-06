import socket
import sys


class Client:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        print(f"connected to ({host}, {port})")

    def messaging(self):
        while True:
            message = input("input message: ")
            encode_msg = message.encode()
            self.socket.sendall(encode_msg)
            replies = self.socket.recv(8096)
            print("Sent: ", repr(replies))


host, port = sys.argv[1], int(sys.argv[2])
client = Client(host, port)
try:
    client.messaging()
except KeyboardInterrupt:
    print("Goobai Awawawa")
