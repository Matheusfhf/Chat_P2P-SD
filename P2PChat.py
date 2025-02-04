import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, Listbox, END
from P2P_SuperPeer import P2P_SuperPeer

# Super Peer (Tracker) Configuration
tracker_host = "127.0.0.1"
tracker_port = 55544

def is_superpeer_running():
    """Check if the Super Peer is already running."""
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(1)
        test_socket.connect((tracker_host, tracker_port))
        test_socket.close()
        return True  # Super Peer is already running
    except:
        return False  # Super Peer is NOT running

# Only start Super Peer if it is not already running
if not is_superpeer_running():
    main_superpeer = P2P_SuperPeer(tracker_host, tracker_port)

def register_with_tracker(host, port, username):
    """Register the peer with the super peer (tracker)."""
    try:
        tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker_socket.connect((tracker_host, tracker_port))
        tracker_socket.send(f"REGISTER {host} {port} {username}".encode('utf-8'))
        tracker_socket.close()
    except Exception as e:
        print(f"Could not register with tracker: {e}")

peers = []  # List of peers connected
usernames = {}  # Dictionary to map peers to their usernames
available_peers = []  # List of discovered peers 

def broadcast_message(raw_message, sender_socket=None):
    for peer in peers:
        if peer != sender_socket:
            try:
                peer.send(raw_message)
            except:
                peers.remove(peer)

def handle_peer_connection(peer_socket):
    try:
        username = peer_socket.recv(1024).decode('utf-8')
        usernames[peer_socket] = username
        join_message = f"{username} has joined the chat!\n".encode('utf-8')
        print(join_message.decode('utf-8'), end="")
        broadcast_message(join_message, sender_socket=peer_socket)

        while True:
            message = peer_socket.recv(1024).decode('utf-8')
            if not message:
                break
            if message == "PING":
                peer_list = ", ".join(usernames.values())
                peer_socket.send(f"PONG: {peer_list}\n".encode('utf-8'))
            else:
                broadcast_message(message.encode('utf-8'), sender_socket=peer_socket)
                chat_box.config(state=tk.NORMAL)
                chat_box.insert(tk.END, f"{message}\n")
                chat_box.config(state=tk.DISABLED)
                message_entry.delete(0, tk.END)
    except:
        print(f"\n{usernames.get(peer_socket, 'A peer')} has disconnected.\n", end="")
    finally:
        peers.remove(peer_socket)
        broadcast_message(f"{usernames.pop(peer_socket, 'A peer')} has left the chat.\n".encode('utf-8'))
        peer_socket.close()

def listen_for_peers(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Listening for peers on {host}:{port}...")

    while True:
        peer_socket, addr = server_socket.accept()
        peers.append(peer_socket)
        threading.Thread(target=handle_peer_connection, args=(peer_socket,), daemon=True).start()

def connect_to_peer(peer_ip, peer_port, username):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((peer_ip, peer_port))
        peers.append(client_socket)
        client_socket.send(username.encode('utf-8'))
        threading.Thread(target=handle_peer_connection, args=(client_socket,), daemon=True).start()
        print(f"Connected to peer at {peer_ip}:{peer_port}")
    except Exception as e:
        print(f"Failed to connect to {peer_ip}:{peer_port} - {e}")

def check_peers():
    """Send a PING message to the super peer and list available peers."""
    global available_peers
    try:
        tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker_socket.connect((tracker_host, tracker_port))
        tracker_socket.send("PING".encode('utf-8'))
        response = tracker_socket.recv(1024).decode('utf-8')
        tracker_socket.close()
        
        available_peers = response.split("\n") if response else []
        peer_listbox.delete(0, END)
        for peer in available_peers:
            peer_listbox.insert(END, peer)
    except Exception as e:
        print(f"Failed to contact super peer: {e}")

def connect_to_selected_peer():
    """Connect to the peer selected from the listbox."""
    selected_index = peer_listbox.curselection()
    if selected_index:
        peer_info = available_peers[selected_index[0]].split()
        if len(peer_info) == 3:
            peer_ip, peer_port, peer_name = peer_info
            connect_to_peer(peer_ip, int(peer_port), peer_name)

def send_message():
    message = message_entry.get()
    if message:
        raw_message = f"{username}: {message}\n".encode('utf-8')
        broadcast_message(raw_message)
        chat_box.config(state=tk.NORMAL)
        chat_box.insert(tk.END, f"You: {message}\n")
        chat_box.config(state=tk.DISABLED)
        message_entry.delete(0, tk.END)

def main():
    global username, chat_box, message_entry, peer_listbox

    username = input("Choose your username: ").strip()
    host = input("Enter your IP (e.g., 127.0.0.1): ").strip()
    port = int(input("Enter your port (e.g., 12345): "))

    register_with_tracker(host, port, username)
    threading.Thread(target=listen_for_peers, args=(host, port), daemon=True).start()
    
    root = tk.Tk()
    root.title("P2P Chat")
    
    info_frame = tk.Frame(root)
    info_frame.pack()

    tk.Label(info_frame, text="Username:", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
    tk.Label(info_frame, text=username, font=("Arial", 14)).pack(side=tk.LEFT)

    tk.Label(info_frame, text="         Address:", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
    tk.Label(info_frame, text=f"{host}:{port}", font=("Arial", 14)).pack(side=tk.LEFT)

    chat_box = scrolledtext.ScrolledText(root, width=50, height=20, state=tk.DISABLED)
    chat_box.pack()

    message_entry = tk.Entry(root, width=50)
    message_entry.pack()

    send_button = tk.Button(root, text="Send", command=send_message)
    send_button.pack()

    check_peers_button = tk.Button(root, text="Check Peers", command=check_peers)
    check_peers_button.pack()

    peer_listbox = Listbox(root, width=50, height=5)
    peer_listbox.pack()

    connect_button = tk.Button(root, text="Connect to Peer", command=connect_to_selected_peer)
    connect_button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()