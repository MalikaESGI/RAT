import cv2
import os
import sys
import time
from datetime import datetime

# Force le programme à se placer dans le bon dossier
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(BASE_DIR) 
OUTPUT_DIR = os.path.join(BASE_DIR, "captures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def capture_webcam_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erreur caméra")
        return
    ret, frame = cap.read()
    if ret:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"webcam_capture_{timestamp}.jpg"
        path = os.path.join(OUTPUT_DIR, filename)
        cv2.imwrite(path, frame)
        print(f"[+] Image sauvegardée : {path}")
    cap.release()

def capture_webcam_video(duration=5):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erreur caméra")
        return
    path = os.path.join(OUTPUT_DIR, "webcam_video.avi")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(path, fourcc, 20.0, (640, 480))
    start = time.time()
    while time.time() - start < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
    cap.release()
    out.release()
    print(f"[+] Vidéo sauvegardée : {path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(0)
    mode = sys.argv[1]
    if mode == "image":
        capture_webcam_image()
    elif mode == "video":
        capture_webcam_video(5)
