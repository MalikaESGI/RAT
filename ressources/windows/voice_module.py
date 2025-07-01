# test_voice.py
import sounddevice as sd
from scipy.io.wavfile import write
import os
import time

DURATION = 5  # secondes
FS = 44100

output_dir = os.path.join(os.getcwd(), "voice")
os.makedirs(output_dir, exist_ok=True)

print("[*] Enregistrement en cours...")
audio = sd.rec(int(DURATION * FS), samplerate=FS, channels=1, dtype='int16')
sd.wait()

filename = f"voice_{int(time.time())}.wav"
path = os.path.join(output_dir, filename)
write(path, FS, audio)

print("[+] Audio enregistré dans :", path)
