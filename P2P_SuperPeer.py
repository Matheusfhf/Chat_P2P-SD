import socket
import threading

class P2P_SuperPeer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peer_list = {}  # { (ip, port): username }
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.start_server()

    def start_server(self):
        """Start the super peer tracker to manage peer connections."""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Super Peer running on {self.host}:{self.port}...")

        threading.Thread(target=self.accept_peers, daemon=True).start()

    def accept_peers(self):
        """Handle incoming peer registrations."""
        while True:
            client_socket, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_peer_connection, args=(client_socket,), daemon=True).start()

    def handle_peer_connection(self, client_socket):
        """Process peer registrations."""
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if data.startswith("REGISTER"):
                _, ip, port, username = data.split()
                self.peer_list[(ip, int(port))] = username
                print(f"Registered: {username} ({ip}:{port})")
        except:
            pass
        finally:
            client_socket.close()
