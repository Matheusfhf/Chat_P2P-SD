import socket
import threading

peers = []  # Lista de peers

def broadcast_message(message, sender_socket=None):
    """Envia mensagens para todos os peers conectados, exceto o remetente."""
    for peer in peers:
        if peer != sender_socket:
            try:
                peer.send(message)
            except:
                peers.remove(peer)

def handle_peer_connection(peer_socket):
    """Gerencia a conexão com um peer."""
    while True:
        try:
            message = peer_socket.recv(1024)
            if not message:
                break
            print(f"\nPeer: {message.decode('utf-8')}\nYou: ", end="")
            broadcast_message(message, peer_socket)
        except:
            peers.remove(peer_socket)
            break
    peer_socket.close()

def listen_for_peers(host, port):
    """Configura o peer para aceitar conexões de outros peers."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Listening for peers on {host}:{port}...")

    while True:
        peer_socket, addr = server_socket.accept()
        print(f"Connected to peer: {addr}")
        peers.append(peer_socket)
        threading.Thread(target=handle_peer_connection, args=(peer_socket,), daemon=True).start()

def connect_to_peer(peer_ip, peer_port):
    """Conecta-se a outro peer."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((peer_ip, peer_port))
        peers.append(client_socket)
        threading.Thread(target=handle_peer_connection, args=(client_socket,), daemon=True).start()
        print(f"Connected to peer at {peer_ip}:{peer_port}")
    except Exception as e:
        print(f"Failed to connect to {peer_ip}:{peer_port} - {e}")

def main():
    print("Welcome to the P2P Chat!")
    host = input("Enter your IP (e.g., 127.0.0.1): ").strip()
    port = int(input("Enter your port (e.g., 12345): "))

    # Inicia o modo de escuta para conexões
    threading.Thread(target=listen_for_peers, args=(host, port), daemon=True).start()

    print("\nCommands:")
    print(" - Type 'connect <IP> <PORT>' to connect to a peer.")
    print(" - Type your message to broadcast to all connected peers.")
    print(" - Type 'exit' to leave the chat.\n")

    while True:
        command = input("You: ").strip()
        if command.lower() == "exit":
            print("Exiting chat...")
            break
        elif command.startswith("connect"):
            _, peer_ip, peer_port = command.split()
            connect_to_peer(peer_ip, int(peer_port))
        else:
            broadcast_message(command.encode('utf-8'))

if __name__ == "__main__":
    main()
