import tkinter as tk
import datetime
import pytz
import re

# Fonction pour obtenir le fuseau horaire sélectionné
def get_selected_timezone():
    selected_timezone = timezone_var.get()
    return pytz.timezone(selected_timezone) if selected_timezone == "Europe/Paris" else pytz.UTC

# Fonction pour analyser une entrée (timestamp, date, now) et appliquer des opérations temporelles
def parse_and_compute_time(input_str):
    try:
        input_str = input_str.strip()

        # Vérifier si l'entrée commence par "now"
        if input_str.lower().startswith("now"):
            base_time = datetime.datetime.now(get_selected_timezone())
            input_str = input_str[3:].strip()  # Retirer "now"
        else:
            # Vérifier si l'entrée est un timestamp en millisecondes ou en secondes
            match = re.match(r"^(\d+)", input_str)
            if match:
                timestamp = int(match.group(1))
                remaining_input = input_str[len(match.group(1)):].strip()  # Récupérer le reste de la chaîne
                
                if timestamp > 10**10:  # Millisecondes -> Secondes
                    timestamp //= 1000
                base_time = datetime.datetime.fromtimestamp(timestamp, tz=get_selected_timezone())

                input_str = remaining_input  # Conserver le reste de la saisie pour appliquer les opérations
            else:
                # Essayer d'interpréter une date au format YYYY-MM-DD HH:MM:SS
                try:
                    base_time = datetime.datetime.strptime(input_str[:19], "%Y-%m-%d %H:%M:%S")
                    base_time = get_selected_timezone().localize(base_time)  # Appliquer le fuseau
                    input_str = input_str[19:].strip()  # Récupérer le reste de la chaîne
                except ValueError:
                    raise ValueError("Format invalide. Utilisez 'YYYY-MM-DD HH:MM:SS', un timestamp ou 'now'.")

        # Appliquer les modifications de temps (+1d, -2h, etc.)
        time_delta = datetime.timedelta()
        matches = re.findall(r"([+-]\d+)([dhms])", input_str)
        for value, unit in matches:
            value = int(value)
            if unit == "d":
                time_delta += datetime.timedelta(days=value)
            elif unit == "h":
                time_delta += datetime.timedelta(hours=value)
            elif unit == "m":
                time_delta += datetime.timedelta(minutes=value)
            elif unit == "s":
                time_delta += datetime.timedelta(seconds=value)

        result_time = base_time + time_delta
        timestamp_ms = int(result_time.timestamp() * 1000)
        formatted_time = result_time.strftime("%Y-%m-%d %H:%M:%S %Z%z")

        update_result_text(f"Timestamp : {timestamp_ms}\nDate : {formatted_time}")

    except ValueError as e:
        update_result_text(f"Erreur : {e}")

# Fonction pour mettre à jour la zone de résultat
def update_result_text(text):
    result_text_widget.config(state=tk.NORMAL)
    result_text_widget.delete(1.0, tk.END)
    result_text_widget.insert(tk.END, text)
    result_text_widget.config(state=tk.DISABLED)

# Création de la fenêtre principale
window = tk.Tk()
window.title("Convertisseur de Timestamp")

# Dimensions et position de la fenêtre
window.geometry("500x300+500+200")

# Menu déroulant pour choisir le fuseau horaire
timezone_label = tk.Label(window, text="Choisissez le fuseau horaire :")
timezone_label.pack(pady=5)

timezone_var = tk.StringVar(window)
timezone_var.set("Europe/Paris")  # Valeur par défaut

timezone_menu = tk.OptionMenu(window, timezone_var, "Europe/Paris", "UTC")
timezone_menu.pack(pady=5)

# Champ de saisie pour la date/timestamp avec opérations
entry_label = tk.Label(window, text="Entrez un timestamp, une date ou 'now' avec opérations :")
entry_label.pack(pady=5)
entry = tk.Entry(window, width=30)
entry.pack(pady=5)

# Bouton pour convertir l'entrée
convert_button = tk.Button(window, text="Convertir", command=lambda: parse_and_compute_time(entry.get()))
convert_button.pack(pady=5)

# Widget Text pour afficher le résultat (sélectionnable)
result_text_widget = tk.Text(window, height=4, width=50, wrap=tk.WORD, font=("Arial", 14))
result_text_widget.pack(pady=20)
result_text_widget.config(state=tk.DISABLED)  # Désactiver l'édition

# Lancer la boucle principale de l'interface graphique
window.mainloop()
