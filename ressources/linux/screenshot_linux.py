import pyautogui
import os
from datetime import datetime
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CAPTURE_DIR = os.path.join(BASE_DIR, "screenshot")
os.makedirs(CAPTURE_DIR, exist_ok=True)

def capture_screen():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    screenshot_path = os.path.join(CAPTURE_DIR, f"screenshot_{timestamp}.jpg")

    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    print(f"[+] Screenshot sauvegardé : {screenshot_path}")
    return screenshot_path

if __name__ == "__main__":
    capture_screen()