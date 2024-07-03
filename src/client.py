import socket


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


client = Client("127.0.0.1", 8080)
try:
    client.messaging()
except KeyboardInterrupt:
    print("Goobai Awawawa")
