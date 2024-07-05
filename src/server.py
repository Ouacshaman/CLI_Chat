import socket
import threading
import re


class Server:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen()
        self.clients = []
        self.client_usernames = {}
        print(f'Server started on {host}:{port}, waiting for connections...')

    def accept(self, convo):
        while True:
            conn, addr = self.sock.accept()
            self.clients.append(conn)
            print(f'Connected by {addr}')
            threading.Thread(target=self.handle_client,
                             args=(conn, convo, addr,)).start()

    def handle_client(self, conn, convo, addr):
        with conn:
            initial_data = conn.recv(65536).decode('utf-8')
            if initial_data.startswith("/username "):
                username = initial_data.split(" ", 1)[1].strip()
                self.client_usernames[conn] = username
                print(f'{username} has connected.')
                self.intro_msg(conn)
            else:
                print("Invalid Username")
                conn.close()
                return
            while True:
                try:
                    data = conn.recv(65536)
                    if not data or "disconnected" in data.decode():
                        self.clients.remove(conn)
                        if conn in self.client_usernames:
                            print(f'{self.client_usernames[conn]}' +
                                  ' has disconnected.')
                            del self.client_usernames[conn]
                        break
                    convo.append(data.decode('utf-8'))
                    self.broadcast(conn, data)
                except Exception as e:
                    print(f'Error handling client {addr}: {e}')
                    break

    def close(self):
        self.sock.close()

    def broadcast(self, conn, data):
        command = self.non_target_cmd(data)
        if command:
            if command[0] == 'pm':
                self.handle_pm(conn, data)
            else:
                print(f"Unknown Command: {command[0]}")
        else:
            for client in self.clients:
                if client != conn:
                    try:
                        decoded = data.decode('utf-8')
                        msg = self.client_usernames[conn] + decoded
                        client.sendall(msg.encode('utf-8'))
                    except Exception as e:
                        print(f'Error Broadcasting to a Client: {e}')
                        self.clients.remove(client)

    def non_target_cmd(self, data):
        decoded = data.decode('utf-8')
        if re.findall(r"^\/(\w+)\s", decoded):
            command = re.findall(r"^\/(\w+)\s", decoded)
            return command
        return

    def intro_msg(self, conn):
        for client in self.clients:
            if client != conn:
                try:
                    msg = f"{self.client_usernames[conn]} has joined"
                    client.sendall(msg.encode('utf-8'))
                except Exception as e:
                    print(f"Error during Intro: {e}")
                    self.clients.remove(client)

    def handle_pm(self, conn, data):
        decoded = data.decode('utf-8')
        args = decoded.split(' ', 2)
        if len(args) < 3:
            return
        command, target_username, message = args
        target_client = None

        for client in self.clients:
            if self.client_usernames[client] == target_username:
                target_client = client
                break

        if target_client:
            try:
                sender_username = self.client_usernames[conn]
                pm_msg = f"(PM from {sender_username}: {message})"
                target_client.sendall(pm_msg.encode('utf-8'))
            except Exception as e:
                print(f"Error sending private message using \\{command}: {e}")
        else:
            try:
                msg = f"User: {target_client} is not available"
                conn.sendall(msg.encode('utf-8'))
            except Exception as e:
                print(f"Error sending unavailability message: {e}")


convo = []
s = Server("127.0.0.1", 8080)

try:
    s.accept(convo)
except KeyboardInterrupt:
    print("Server Ended")
    s.close()


for item in convo:
    lst = item.split(" ")
    name = lst.pop()
    msg = " ".join(lst)
    print(f"{name}: {msg}")
