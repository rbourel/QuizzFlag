import tkinter as tk
from tkinter import Tk, Label, Button, messagebox, Entry, Radiobutton, Frame, Toplevel, Scrollbar, Canvas
import random
from PIL import Image, ImageTk



# Fonction pour lire le fichier des drapeaux et créer un dictionnaire
def load_flags_from_file(filename):
    flags_dict = {}
    capital_dict = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            country, path, capital = line.strip().split(',')
            flags_dict[country] = path
            capital_dict[country] = capital
    return flags_dict, capital_dict

# Charger les drapeaux depuis le fichier
flags, capital = load_flags_from_file("flags.txt")

class FlagQuiz:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz sur les drapeaux")

        # Ajouter un bouton pour ouvrir la page de tous les pays
        self.all_countries_button = tk.Button(root, text="Voir tous les pays", font=("Arial", 14), command=self.show_all_countries)
        self.all_countries_button.pack(pady=10)

        # Initialiser les composants de l'interface
        self.question_label = tk.Label(root, text="Quel est le drapeau de ... ?", font=("Arial", 16))
        self.question_label.pack(pady=20)

        self.score = 0  # Score total
        self.streak = 0  # Compteur de réponses réussies d'affilée
        self.num_flags = 4
        self.current_question_type = "flag"  # Nouveau: type de question ("flag" ou "capital")


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

        # Créer une Frame pour les boutons
        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack()

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
            button.grid_forget()
        self.buttons = []

        # Créer les nouveaux boutons pour les drapeaux
        for i in range(self.num_flags):
            button = tk.Button(self.buttons_frame, text="", font=("Arial", 24), width=120, height=60, command=lambda i=i: self.check_answer(i))
            button.grid(row=i//3, column=i%3, padx=10, pady=10)  # 3 boutons par ligne
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
        if self.current_question_type == "flag":
            self.ask_flag_question()
        else:
            self.ask_capital_question()

    def ask_flag_question(self):
        self.correct_country = random.choice(list(flags.keys()))

        other_countries = list(flags.keys())
        other_countries.remove(self.correct_country)
        self.choices = random.sample(other_countries, self.num_flags-1) + [self.correct_country]

        random.shuffle(self.choices)

        self.question_label.config(text=f"Quel est le drapeau de {self.correct_country} ?")

        self.flag_images = [None] * self.num_flags

        for i, country in enumerate(self.choices):
            image = Image.open(flags[country])
            image = image.resize((120, 80), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)

            self.flag_images[i] = photo
            self.buttons[i].config(image=photo, text="", font=("Arial", 24), width=120, height=60)

        self.result_label.config(text="")
        self.current_question_type = "capital"  # Passer à la question sur la capitale après celle-ci

    def ask_capital_question(self):
        self.correct_country = random.choice(list(capital.keys()))

        other_countries = list(capital.keys())
        other_countries.remove(self.correct_country)
        self.choices = random.sample(other_countries, self.num_flags-1) + [self.correct_country]

        random.shuffle(self.choices)

        self.question_label.config(text=f"Quelle est la capitale de {self.correct_country} ?")

        for i, country in enumerate(self.choices):
            self.buttons[i].config(text=capital[country], image='', font=("Arial", 12), width=20, height=2)

        self.result_label.config(text="")
        self.current_question_type = "flag"  # Revenir à la question sur le drapeau après celle-ci

    def check_answer(self, index):
        if self.choices[index] == self.correct_country:
            self.score += 1
            self.streak += 1
            self.result_label.config(text="Bonne réponse!", fg="green")
            self.next_question()
        else:
            self.streak = 0
            self.result_label.config(text=f"Mauvaise réponse. Le bon pays est {self.correct_country} avec pour capitale {capital[self.correct_country]}", fg="red")

        self.streak_label.config(text=f"Réponses réussies d'affilée : {self.streak}")

    def show_all_countries(self):
        # Créer une nouvelle fenêtre pour afficher la liste de tous les pays
        all_countries_window = Toplevel(self.root)
        all_countries_window.title("Liste des pays avec leur drapeau et capitale")

        # Créer un Canvas pour permettre le défilement
        canvas = Canvas(all_countries_window)
        canvas.pack(side="left", fill="both", expand=True)

        # Ajouter une barre de défilement verticale
        scrollbar = Scrollbar(all_countries_window, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Configurer le Canvas pour utiliser la barre de défilement
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Créer un Frame qui sera contenu dans le Canvas
        scrollable_frame = Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Attacher le Frame scrollable au Canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Ajouter les drapeaux et les capitales des pays
        for country, flag_path in flags.items():
            frame = Frame(scrollable_frame)
            frame.pack(fill="x", pady=5)

            # Afficher le drapeau
            image = Image.open(flag_path)
            image = image.resize((50, 30), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            label_flag = tk.Label(frame, image=photo)
            label_flag.image = photo  # Garder une référence pour éviter que l'image soit supprimée
            label_flag.pack(side="left", padx=10)

            # Afficher le nom du pays
            label_country = tk.Label(frame, text=country, font=("Arial", 12))
            label_country.pack(side="left", padx=10)

            # Afficher la capitale du pays
            label_capital = tk.Label(frame, text=capital[country], font=("Arial", 12))
            label_capital.pack(side="left", padx=10)


if __name__ == "__main__":
    root = tk.Tk()
    quiz = FlagQuiz(root)
    root.mainloop()