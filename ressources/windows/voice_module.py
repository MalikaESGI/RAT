import sounddevice as sd
from scipy.io.wavfile import write
import os
import tempfile
import time

DURATION = 10  # secondes

def record_voice(duration=DURATION):
    fs = 44100  # fréquence d’échantillonnage
    print("[+] Enregistrement vocal en cours...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    temp_file = os.path.join(tempfile.gettempdir(), f"recording_{int(time.time())}.wav")
    write(temp_file, fs, audio)
    return temp_file

def send_file(file_path, sock):
    try:
        filename = os.path.basename(file_path)
        filesize = os.path.getsize(file_path)
        header = f"voice:{filename}:{filesize}".encode().ljust(128)
        sock.sendall(header)

        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                sock.sendall(chunk)
        print(f"[+] Fichier audio envoyé : {filename}")
    except Exception as e:
        print(f"[!] Erreur d'envoi : {e}")

def record_and_send(sock):
    try:
        temp_wav = record_voice()
        send_file(temp_wav, sock)
        os.remove(temp_wav)
        print("[+] Fichier temporaire supprimé.")
    except Exception as e:
        print(f"[!] Erreur dans record_and_send : {e}")
