import socket
import threading
import tkinter as tk
from P2P_SuperPeer import P2P_SuperPeer
from tkinter import scrolledtext, Listbox, END, messagebox

tracker_host = "192.168.0.207"  # SEU IPV4 AQUI
tracker_port = 5055

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def is_superpeer_running():
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(1)
        test_socket.connect((tracker_host, tracker_port))
        test_socket.close()
        return True
    except:
        return False

if not is_superpeer_running():
    main_superpeer = P2P_SuperPeer(tracker_host, tracker_port)

def register_with_tracker(host, port, username):
    try:
        tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker_socket.connect((tracker_host, tracker_port))
        tracker_socket.send(f"REGISTER {host} {port} {username}".encode('utf-8'))
        tracker_socket.close()
    except:
        print("Não foi possível registrar o tracker")

# Lista de peers conectados
peers = []
available_peers = []

def listen_for_peers(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Escutando peers em {host}:{port}...")
    while True:
        peer_socket, addr = server_socket.accept()
        peers.append(peer_socket)
        threading.Thread(target=handle_peer_connection, args=(peer_socket,), daemon=True).start()

def handle_peer_connection(peer_socket):
    try:
        while True:
            message = peer_socket.recv(1024).decode('utf-8')
            if not message:
                break
            chat_box.config(state=tk.NORMAL)
            chat_box.insert(tk.END, message)
            chat_box.config(state=tk.DISABLED)
    except:
        pass
    finally:
        peer_socket.close()
        peers.remove(peer_socket)

def check_peers():
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
            elements = peer.split(' ')
            if len(elements) == 3:
                string = f"IP: {elements[0]}:{elements[1]}  |  Usuario: {elements[2]}"
                peer_listbox.insert(END, string)
            else:
                peer_listbox.insert(END, peer)
    except:
        messagebox.showinfo("Erro", "Falha ao conectar no Super Peer")
        print("Falha ao conectar no Super Peer")

def connect_to_selected_peer():
    selected_index = peer_listbox.curselection()
    if selected_index:
        peer_info = available_peers[selected_index[0]].split()
        if len(peer_info) == 3:
            peer_ip, peer_port, _ = peer_info
            
            # Verificar se não está tentando conectar a si mesmo
            if peer_ip == host and int(peer_port) == port:
                messagebox.showinfo("Erro", "Não é possível conectar a si mesmo.")
                return
            
            # Verificar se o peer já está na lista de conexões
            for peer in peers:
                peer_ip_existing, peer_port_existing = peer.getpeername()
                if peer_ip_existing == peer_ip and peer_port_existing == int(peer_port):
                    messagebox.showinfo("Erro", "Já está conectado a esse peer.")
                    return
            
            connect_to_peer(peer_ip, int(peer_port))

def connect_to_peer(peer_ip, peer_port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((peer_ip, peer_port))
        peers.append(client_socket)
        threading.Thread(target=handle_peer_connection, args=(client_socket,), daemon=True).start()
        messagebox.showinfo("Sucesso", f"Conectado com sucesso no endereço: {peer_ip}:{peer_port}")
    except:
        messagebox.showinfo("Erro", f"Falha pra conectar em {peer_ip}:{peer_port}")
        print(f"Falha pra conectar em {peer_ip}:{peer_port}")

def send_message():
    message = message_entry.get()
    if message:
        raw_message = f"{username}: {message}\n".encode('utf-8')
        for peer in peers:
            peer.send(raw_message)
        chat_box.config(state=tk.NORMAL)
        chat_box.insert(tk.END, f"You: {message}\n")
        chat_box.config(state=tk.DISABLED)
        message_entry.delete(0, tk.END)

def main():
    global username, chat_box, message_entry, peer_listbox, host, port
    username = input("Escolha seu username: ").strip()
    host = get_local_ip()
    port = int(input("Escolha uma porta(Exemplo: 5050): "))
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
    tk.Button(root, text="Enviar", command=send_message).pack()
    tk.Button(root, text="Atualizar Peers", command=check_peers).pack()
    peer_listbox = Listbox(root, width=50, height=5)
    peer_listbox.pack()
    tk.Button(root, text="Conectar ao Peer", command=connect_to_selected_peer).pack()
    root.mainloop()

if __name__ == "__main__":
    main()
