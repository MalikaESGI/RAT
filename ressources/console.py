import tkinter as tk
from tkinter import scrolledtext
import sqlite3

# Connexion à la base de données
DB_PATH = "/home/kali/PA/bdd/rat.db"

# Fonction pour exécuter des commandes
def execute_command():
    command = command_entry.get()
    output_text.insert(tk.END, f"> {command}\n")
    if command == "list_targets":
        list_targets()
    elif command == "exit":
        root.quit()
    else:
        output_text.insert(tk.END, "Commande non reconnue.\n")
    command_entry.delete(0, tk.END)

# Commande pour lister les cibles
def list_targets():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, ip_address, hostname, os FROM targets")
        rows = cursor.fetchall()
        conn.close()

        if rows:
            output_text.insert(tk.END, f"{'ID':<5}{'IP':<20}{'Hostname':<15}{'OS':<20}\n")
            output_text.insert(tk.END, "-" * 60 + "\n")
            for row in rows:
                output_text.insert(tk.END, f"{row[0]:<5}{row[1]:<20}{row[2]:<15}{row[3]:<20}\n")
        else:
            output_text.insert(tk.END, "Aucune cible enregistrée.\n")
    except Exception as e:
        output_text.insert(tk.END, f"Erreur lors de la récupération des cibles : {e}\n")

# Initialisation de la fenêtre Tkinter
root = tk.Tk()
root.title("Console RAT")

# Zone de texte pour afficher les résultats
output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
output_text.pack(padx=10, pady=10)

# Champ pour entrer les commandes
command_entry = tk.Entry(root, width=80)
command_entry.pack(padx=10, pady=5)

# Bouton pour exécuter les commandes
execute_button = tk.Button(root, text="Exécuter", command=execute_command)
execute_button.pack(pady=5)

# Boucle principale Tkinter
root.mainloop()
