# screenshot.py

import win32api
import win32con
import win32gui
import win32ui
from PIL import Image
from datetime import datetime
import os
import sys
import time

# Répertoire d'exécution
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CAPTURE_DIR = os.path.join(BASE_DIR, "captures")
os.makedirs(CAPTURE_DIR, exist_ok=True)

def get_dimensions():
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    return width, height, left, top

def capture_screen():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    bmp_path = os.path.join(CAPTURE_DIR, f"screenshot_{timestamp}.bmp")
    jpg_path = os.path.join(CAPTURE_DIR, f"screenshot_{timestamp}.jpg")

    hdesktop = win32gui.GetDesktopWindow()
    width, height, left, top = get_dimensions()

    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)
    mem_dc = img_dc.CreateCompatibleDC()

    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(img_dc, width, height)
    mem_dc.SelectObject(bmp)
    mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)
    bmp.SaveBitmapFile(mem_dc, bmp_path)

    mem_dc.DeleteDC()
    win32gui.DeleteObject(bmp.GetHandle())

    with Image.open(bmp_path) as img:
        img.save(jpg_path, "JPEG", quality=50)

    os.remove(bmp_path)
    print(f"[+] Screenshot sauvegardé : {jpg_path}")
    return jpg_path

if __name__ == "__main__":
    # Support du mode delay:5
    if len(sys.argv) == 2 and sys.argv[1].startswith("delay:"):
        try:
            delay = int(sys.argv[1].split(":")[1])
            print(f"[~] Attente de {delay} secondes avant capture...")
            time.sleep(delay)
        except:
            pass
    capture_screen()
