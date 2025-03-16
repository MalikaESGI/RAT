import socket
import time
import os
from datetime import datetime

HOST = '0.0.0.0'  
PORT = 5001  
CAPTURE_DIR = "captures/"  # Dossier pour stocker les captures

# Créer le dossier de captures s'il n'existe pas
os.makedirs(CAPTURE_DIR, exist_ok=True)

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"[+] En attente d'une connexion sur {HOST}:{PORT}...")

        conn, addr = server.accept()
        with conn:
            print(f"[+] Connexion établie avec {addr}")
            
            while True:
                print("\nMenu:")
                print("1 - Prendre une capture d'écran complète")
                print("2 - Prendre une capture d'écran après un délai")
                print("3 - Quitter")
                
                choice = input("Choisissez une option: ")
                
                if choice == "1":
                    conn.sendall(b"screenshot")
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{CAPTURE_DIR}received_screenshot_{timestamp}.png"
                    with open(filename, "wb") as f:
                        while True:
                            data = conn.recv(4096)
                            if not data:
                                break
                            f.write(data)
                    print(f"[+] Capture reçue : {filename}")

                elif choice == "2":
                    delay = int(input("Entrez le délai en secondes: "))
                    conn.sendall(f"delay:{delay}".encode())
                    print(f"[+] Capture planifiée après {delay} secondes...")
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{CAPTURE_DIR}received_screenshot_{timestamp}.png"
                    with open(filename, "wb") as f:
                        while True:
                            data = conn.recv(4096)
                            if not data:
                                break
                            f.write(data)
                    print(f"[+] Capture reçue : {filename}")
                
                elif choice == "3":
                    conn.sendall(b"exit")
                    print("[+] Fermeture de la connexion")
                    break
                
                else:
                    print("Option invalide, réessayez.")

if __name__ == "__main__":
    start_server()
