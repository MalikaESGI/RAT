import cv2
import socket
import json
import os
import time

# Configuration du serveur
SERVER_IP = "192.168.56.1"  # Remplace par l'IP de ton serveur
SERVER_PORT = 4444

# Dossier temporaire pour sauvegarder les fichiers capturés
OUTPUT_DIR = "captures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fonction pour capturer une image depuis la webcam
def capture_webcam_image():
    cap = cv2.VideoCapture(0)  # Ouvre la webcam (0 pour la webcam par défaut)
    if not cap.isOpened():
        print("Erreur : Impossible d'accéder à la webcam.")
        return None

    ret, frame = cap.read()
    if ret:
        image_path = os.path.join(OUTPUT_DIR, "webcam_capture.jpg")
        cv2.imwrite(image_path, frame)  # Sauvegarde l'image
        print(f"Image capturée et sauvegardée à : {image_path}")
    else:
        print("Erreur : Impossible de capturer une image.")
        image_path = None

    cap.release()
    return image_path

# Fonction pour capturer une vidéo depuis la webcam
def capture_webcam_video(duration=5):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erreur : Impossible d'accéder à la webcam.")
        return None

    video_path = os.path.join(OUTPUT_DIR, "webcam_video.avi")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec vidéo
    out = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480))  # 20 FPS, 640x480

    print(f"Enregistrement de la vidéo pendant {duration} secondes...")
    start_time = time.time()
    while int(time.time() - start_time) < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
        else:
            print("Erreur : Impossible de lire la vidéo.")
            break

    cap.release()
    out.release()
    print(f"Vidéo capturée et sauvegardée à : {video_path}")
    return video_path

# Fonction pour envoyer un fichier (image ou vidéo) au serveur
def send_file_to_server(file_path, file_type):
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "rb") as file:
                file_data = file.read()

            # Préparer les données à envoyer
            payload = json.dumps({
                "type": file_type,  # "webcam_capture" pour les images, "webcam_video" pour les vidéos
                "filename": os.path.basename(file_path),
                "data": file_data.hex()  # Encode les données en hexadécimal
            })

            # Envoyer les données au serveur
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((SERVER_IP, SERVER_PORT))
            client_socket.send(payload.encode('utf-8'))
            client_socket.close()

            print(f"Fichier {os.path.basename(file_path)} envoyé au serveur.")
        except Exception as e:
            print(f"Erreur lors de l'envoi du fichier au serveur : {e}")
    else:
        print("Aucun fichier à envoyer ou le fichier n'existe pas.")

# Fonction principale
def main():
    while True:
        print("\nOptions :")
        print("1. Capturer une image depuis la webcam")
        print("2. Capturer une vidéo depuis la webcam")
        print("3. Quitter")
        choice = input("Choisissez une option (1/2/3) : ").strip()

        if choice == "1":
            # Capturer et envoyer une image
            image_path = capture_webcam_image()
            if image_path:
                send_file_to_server(image_path, "webcam_capture")

        elif choice == "2":
            # Capturer et envoyer une vidéo
            duration = int(input("Durée de la vidéo (en secondes) : "))
            video_path = capture_webcam_video(duration=duration)
            if video_path:
                send_file_to_server(video_path, "webcam_video")

        elif choice == "3":
            print("Fermeture du programme.")
            break

        else:
            print("Choix invalide. Veuillez réessayer.")

if __name__ == "__main__":
    main()
