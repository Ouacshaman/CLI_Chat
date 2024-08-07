import socket
import threading
import re
import json
import sys


class Server:
    def __init__(self, host, port, file_path):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen()
        self.clients = []
        self.client_usernames = {}
        self.file_path_users = ("/Users/shihong/D3v3lop/Code" +
                                "/Create/proj06/chat_app/src/users.json")
        print(f'Server started on {host}:{port}, waiting for connections...')

    def accept(self, convo):
        while True:
            conn, addr = self.sock.accept()
            conn.settimeout(360)
            self.clients.append(conn)
            print(f'Connected by {addr}')
            threading.Thread(target=self.handle_client,
                             args=(conn, convo, addr,)).start()

    def handle_client(self, conn, convo, addr):
        try:
            initial_data = conn.recv(65536).decode('utf-8')
            if initial_data.startswith("/username "):
                split_data = initial_data.split(" ", 2)
                username = split_data[1].strip()
                password = split_data[2].strip()
                json_data = load_json(self.file_path_users)
                if username in json_data:
                    if json_data.get(username) == password:
                        self.client_usernames[conn] = username
                        print(f'{username} has connected.')
                        self.intro_msg(conn)
                    else:
                        self.password_failed(conn)
                else:
                    data = {username: password}
                    write_json(self.file_path_users, data)
                    self.client_usernames[conn] = username
                    print(f'{username} registered')
                    self.intro_msg(conn)
            else:
                print("Invalid Username")
                return
            while True:
                try:
                    data = conn.recv(65536)
                    if not data or "disconnected" in data.decode():
                        break
                    convo.append(self.client_usernames[conn]
                                 + data.decode('utf-8') + ' \n ')
                    self.broadcast(conn, data)
                except socket.timeout:
                    print(f"Connection to {conn.getpeername()} timed out.")
                    break
                except Exception as e:
                    print(f'Error handling client {addr}: {e}')
                    break
        finally:
            self.cleanup_connection(conn)

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
                        msg = (self.client_usernames[conn] + ": " +
                               decoded + " \n ")
                        convo.append(msg)
                        client.sendall(msg.encode('utf-8'))
                    except Exception:
                        print(f'Client {client} disconnected ' +
                              'while broadcasting. \n ')
                        self.cleanup_connection(client)

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
                    msg = f"{self.client_usernames[conn]} has joined \n "
                    convo.append(msg)
                    client.sendall(msg.encode('utf-8'))
                except Exception as e:
                    print(f"Error during Intro: {e}")
                    self.cleanup_connection(client)

    def password_failed(self, conn):
        try:
            msg = "incorrect password \n "
            convo.append(msg)
            conn.sendall(msg.encode('utf-8'))
        except Exception as e:
            print(f"failed to send password failure: {e}")
        finally:
            self.cleanup_connection(conn)

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
                pm_msg = f"(PM from {sender_username}: {message}) \n "
                convo.append(pm_msg)
                target_client.sendall(pm_msg.encode('utf-8'))
            except ValueError:
                conn.sendall("Invalid private message format. Use:" +
                             " /pm <username> <message>".encode('utf-8'))
            except Exception as e:
                print(f"Error sending private message using \\{command}: {e}")
                self.cleanup_connection(conn)
        else:
            try:
                msg = f"User: {target_client} is not available"
                conn.sendall(msg.encode('utf-8'))
            except Exception as e:
                print(f"Error sending unavailability message: {e}")

    def cleanup_connection(self, conn):
        if conn in self.clients:
            self.clients.remove(conn)
        if conn in self.client_usernames:
            username = self.client_usernames.pop(conn)
            print(f'{username} has disconnected.')
        try:
            conn.close()
        except Exception as e:
            print(f'Error closing connection {conn}: {e}')


def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_json(file_path, data):
    file_data = load_json(file_path)
    file_data.update(data)
    with open(file_path, 'w') as file:
        json.dump(file_data, file, indent=4)


convo = []
host, port, file_path = sys.argv[1], int(sys.argv[2]), sys.argv[3]
s = Server(host, port, file_path)

try:
    s.accept(convo)
except KeyboardInterrupt:
    print("Server Ended")
    s.close()


for item in convo:
    print(item)
