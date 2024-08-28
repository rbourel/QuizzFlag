import tkinter as tk
from tkinter import Tk, Label, Button, messagebox, Entry, Radiobutton, Frame
import random
from PIL import Image, ImageTk



# Fonction pour lire le fichier des drapeaux et créer un dictionnaire
def load_flags_from_file(filename):
    flags_dict = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            country, path = line.strip().split(',')
            flags_dict[country] = path
    return flags_dict

# Charger les drapeaux depuis le fichier
flags = load_flags_from_file("flags.txt")

class FlagQuiz:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz sur les drapeaux")

        # Initialiser les composants de l'interface
        self.question_label = tk.Label(root, text="Quel est le drapeau de ... ?", font=("Arial", 16))
        self.question_label.pack(pady=20)

        self.score = 0  # Score total
        self.streak = 0  # Compteur de réponses réussies d'affilée
        self.num_flags = 4

        # Frame pour le sélecteur de nombre de drapeaux
        self.frame = tk.Frame(root)
        self.frame.pack(pady=10)

        # Label et champ de saisie pour entrer un nombre de drapeaux personnalisé
        self.num_flags_label = tk.Label(self.frame, text="Nombre de drapeaux :")
        self.num_flags_label.pack(side="left")

        self.num_flags_entry = tk.Entry(self.frame, width=5)
        self.num_flags_entry.insert(0, "4")  # Valeur par défaut
        self.num_flags_entry.pack(side="left")

        self.submit_button = tk.Button(self.frame, text="Valider", command=self.update_num_flags)
        self.submit_button.pack(side="left")

        # Label pour afficher le compteur de réponses réussies d'affilée
        self.streak_label = tk.Label(root, text=f"Réponses réussies d'affilée : {self.streak}", font=("Helvetica", 12))
        self.streak_label.pack()

        self.buttons = []
        self.flag_images = []

        self.create_buttons()
        self.result_label = tk.Label(root, text="", font=("Arial", 14))
        self.result_label.pack(pady=20)

        self.next_button = tk.Button(root, text="Prochaine question", font=("Arial", 14), command=self.next_question)
        self.next_button.pack(pady=20)

        self.next_question()

    def create_buttons(self):
        # Effacer les boutons existants s'ils existent
        for button in self.buttons:
            button.pack_forget()
        self.buttons = []

        # Créer les nouveaux boutons pour les drapeaux
        for _ in range(self.num_flags):
            button = tk.Button(self.root, text="", font=("Arial", 24), width=120, height=60, command=lambda i=len(self.buttons): self.check_answer(i))
            button.pack(pady=10)
            self.buttons.append(button)

    def update_num_flags(self):
        try:
            # Essayer de convertir la saisie en entier
            new_num_flags = int(self.num_flags_entry.get())
            if new_num_flags < 1:
                raise ValueError("Le nombre de drapeaux doit être au moins 1.")
            self.num_flags = new_num_flags
            self.create_buttons()  # Mettre à jour les boutons en fonction du nouveau nombre de drapeaux
            self.next_question()  # Recharger les questions après changement du nombre de drapeaux
        except ValueError as e:
            messagebox.showerror("Erreur", f"Veuillez entrer un nombre valide de drapeaux.\n{e}")

    def next_question(self):
        # Choisir un pays correct aléatoirement
        self.correct_country = random.choice(list(flags.keys()))

        # Créer une liste des autres pays pour les choix
        other_countries = list(flags.keys())
        other_countries.remove(self.correct_country)
        self.choices = random.sample(other_countries, self.num_flags-1) + [self.correct_country]

        # Mélanger les choix
        random.shuffle(self.choices)

        # Mettre à jour l'interface avec la nouvelle question
        self.question_label.config(text=f"Quel est le drapeau de {self.correct_country} ?")

        # Effacer les images des boutons précédents
        self.flag_images = [None] * self.num_flags

        for i, country in enumerate(self.choices):
            # Charger l'image du drapeau
            image = Image.open(flags[country])
            image = image.resize((120, 80), Image.LANCZOS)  # Redimensionner si nécessaire
            photo = ImageTk.PhotoImage(image)

            self.flag_images[i] = photo  # Conserver la référence à l'image
            self.buttons[i].config(image=photo, text="")  # Mettre à jour le bouton avec l'image

        # Masquer les boutons non utilisés si le nombre de drapeaux est réduit
        for j in range(len(self.choices), len(self.buttons)):
            self.buttons[j].pack_forget()

        self.result_label.config(text="")

    def check_answer(self, index):
        if self.choices[index] == self.correct_country:
            self.score += 1
            self.streak += 1
            self.result_label.config(text="Bonne réponse!", fg="green")
            self.next_question()
        else:
            self.streak = 0
            self.result_label.config(text=f"Mauvaise réponse. Le bon drapeau était {self.correct_country}.", fg="red")

        self.streak_label.config(text=f"Réponses réussies d'affilée : {self.streak}")

if __name__ == "__main__":
    root = tk.Tk()
    quiz = FlagQuiz(root)
    root.mainloop()