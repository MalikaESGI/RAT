import socket
import mss
import pickle
import struct
import time

SERVER_IP = "192.168.206.1"
REMOTE_PORT = 5555

def stream_screen():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, REMOTE_PORT))
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Full screen
            while True:
                img = sct.grab(monitor)
                frame = {
                    'size': (img.width, img.height),
                    'rgb': img.rgb
                }
                data = pickle.dumps(frame)
                s.sendall(struct.pack("!I", len(data)) + data)
                time.sleep(0.1)  # 10 FPS

if __name__ == "__main__":
    stream_screen()
