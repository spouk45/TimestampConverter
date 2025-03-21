import tkinter as tk
import datetime
import pytz
import re

# Fonction pour obtenir le fuseau horaire sélectionné
def get_selected_timezone():
    selected_timezone = timezone_var.get()
    return pytz.timezone(selected_timezone) if selected_timezone == "Europe/Paris" else pytz.UTC

# Fonction pour analyser une entrée et appliquer des opérations temporelles
def parse_and_compute_time(input_str):
    try:
        input_str = input_str.strip()

        # Vérifier si l'entrée commence par "now"
        if input_str.lower().startswith("now"):
            base_time = datetime.datetime.now(get_selected_timezone())
            input_str = input_str[3:].strip()  # Retirer "now"
        else:
            # Vérifier si l'entrée est une date complète "YYYY-MM-DD HH:MM:SS"
            date_match = re.match(r"^\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}:\d{2})?", input_str)
            fr_date_match = re.match(r"^\d{2}/\d{2}/\d{4}(?: \d{2}:\d{2}:\d{2})?", input_str)
            
            if date_match:
                date_str = date_match.group()
                if " " not in date_str:
                    date_str += " 00:00:00"  # Ajouter l'heure si absente
                base_time = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                base_time = get_selected_timezone().localize(base_time)
                input_str = input_str[len(date_match.group()):].strip()
            elif fr_date_match:
                date_str = fr_date_match.group()
                if " " not in date_str:
                    date_str += " 00:00:00"
                base_time = datetime.datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
                base_time = get_selected_timezone().localize(base_time)
                input_str = input_str[len(fr_date_match.group()):].strip()
            else:
                # Vérifier si l'entrée est un timestamp
                match = re.match(r"^(\d+)", input_str)
                if match:
                    timestamp = int(match.group(1))
                    remaining_input = input_str[len(match.group(1)):].strip()
                
                    if timestamp > 10**10:  # Millisecondes -> Secondes
                        timestamp //= 1000
                    base_time = datetime.datetime.fromtimestamp(timestamp, tz=get_selected_timezone())

                    input_str = remaining_input
                else:
                    raise ValueError("Format invalide. Utilisez 'YYYY-MM-DD', 'JJ/MM/AAAA', un timestamp ou 'now'.")

        # Appliquer les modifications temporelles (+1d, -2h, etc.)
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

# Fonction pour valider avec la touche Entrée
def on_enter_pressed(event):
    parse_and_compute_time(entry.get())

# Création de la fenêtre principale
window = tk.Tk()
window.title("Convertisseur de Timestamp")
window.geometry("300x230+500+200")  # Taille réduite

# Menu déroulant pour choisir le fuseau horaire
timezone_label = tk.Label(window, text="Fuseau horaire :")
timezone_label.pack(pady=2)

timezone_var = tk.StringVar(window)
timezone_var.set("Europe/Paris")  # Valeur par défaut
timezone_menu = tk.OptionMenu(window, timezone_var, "Europe/Paris", "UTC")
timezone_menu.pack(pady=2)

# Champ de saisie pour la date/timestamp avec opérations
entry_label = tk.Label(window, text="Date, timestamp ou 'now' :")
entry_label.pack(pady=2)
entry = tk.Entry(window, width=30)
entry.pack(pady=2)
entry.bind("<Return>", on_enter_pressed)  # Capture de la touche Entrée

# Bouton pour convertir l'entrée
convert_button = tk.Button(window, text="Convertir", command=lambda: parse_and_compute_time(entry.get()))
convert_button.pack(pady=2)

# Widget Text pour afficher le résultat
result_text_widget = tk.Text(window, height=3, width=50, wrap=tk.WORD, font=("Arial", 12))
result_text_widget.pack(pady=10)
result_text_widget.config(state=tk.DISABLED)

# Lancer l'interface graphique
window.mainloop()
