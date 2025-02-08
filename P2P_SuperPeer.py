import socket
import threading

class P2P_SuperPeer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peer_list = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.start_server()

    def start_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Super Peer running on {self.host}:{self.port}...")
        threading.Thread(target=self.accept_peers, daemon=True).start()

    def accept_peers(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_peer_connection, args=(client_socket,), daemon=True).start()

    def handle_peer_connection(self, client_socket):
        try:
            data = client_socket.recv(1024).decode('utf-8').strip()
            if data.startswith("REGISTER"):
                _, ip, port, username = data.split()
                self.peer_list[(ip, int(port))] = username
                client_socket.send("REGISTERED".encode('utf-8'))
            elif data == "PING":
                peer_list_str = "\n".join([f"{ip} {port} {username}" for (ip, port), username in self.peer_list.items()])
                client_socket.send(peer_list_str.encode('utf-8'))
        except:
            pass
        finally:
            client_socket.close()
