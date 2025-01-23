import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np
import pandas as pd
from tkinter import Tk, filedialog
import os
import shutil

# Funzione per caricare un file LUT
def load_lut():
    Tk().withdraw()  # Nascondi la finestra principale di Tkinter
    file_path = filedialog.askopenfilename(title="Seleziona un file LUT", filetypes=[("LUT Files", "*.lut")])
    if file_path:
        lut_data = pd.read_csv(file_path, sep="|", header=None, names=["RPM", "Torque_NM"])
        # Creazione di un backup
        create_backup(file_path)
        return lut_data, file_path
    else:
        print("Nessun file selezionato.")
        return None, None

# Funzione per creare un backup del file
def create_backup(file_path):
    backup_path = file_path + ".backup"
    if not os.path.exists(backup_path):
        shutil.copy(file_path, backup_path)
        print(f"Backup creato: {backup_path}")
    else:
        print(f"Backup già esistente: {backup_path}")

# Funzione per salvare il file LUT
def save_lut(data, path=None):
    if path is None:
        Tk().withdraw()
        path = filedialog.asksaveasfilename(title="Salva il file LUT", defaultextension=".lut", filetypes=[("LUT Files", "*.lut")])
    if path:
        data.to_csv(path, sep="|", index=False, header=False)
        print(f"File salvato: {path}")
    else:
        print("Salvataggio annullato.")

# Funzione per aggiornare i punti trascinandoli
class DraggablePoints:
    def __init__(self, scatter, torque):
        self.scatter = scatter
        self.torque = torque
        self.selected_index = None
        self.cid_press = scatter.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_release = scatter.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = scatter.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        if event.inaxes != self.scatter.axes: return
        contains, ind = self.scatter.contains(event)
        if contains:
            self.selected_index = ind["ind"][0]

    def on_release(self, event):
        self.selected_index = None
        self.scatter.figure.canvas.draw()

    def on_motion(self, event):
        if self.selected_index is None: return
        if event.inaxes != self.scatter.axes: return
        self.torque[self.selected_index] = event.ydata
        self.scatter.set_offsets(np.c_[rpm, self.torque])
        self.scatter.figure.canvas.draw()

# Funzione per aggiornare il grafico ricaricando il file temporaneo
def reload_temp_lut():
    temp_path = os.path.join(os.path.dirname(file_path), "temp_lut.lut")
    if os.path.exists(temp_path):
        temp_data = pd.read_csv(temp_path, sep="|", header=None, names=["RPM", "Torque_NM"])
        return temp_data
    else:
        print("File temporaneo non trovato.")
        return None

# Caricamento iniziale del file LUT
lut_data, file_path = load_lut()
if lut_data is not None:
    rpm = lut_data["RPM"].values
    torque = lut_data["Torque_NM"].values

    # Creazione del grafico interattivo
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.canvas.manager.set_window_title("AC Lut Visual Editor")
    plt.subplots_adjust(bottom=0.5)
    scatter = ax.scatter(rpm, torque, color='red', label="Torque Points")
    line, = ax.plot(rpm, torque, 'o-', label="Torque Curve")
    draggable = DraggablePoints(scatter, torque)

    # Imposta il titolo dinamico con il nome del file
    file_name = os.path.basename(file_path)
    ax.set_title(f"Modifica Interattiva della Curva di {file_name}")

    ax.set_xlabel("RPM")
    ax.set_ylabel("Torque (Nm)")
    ax.legend()
    ax.grid(True)

    # Funzione per salvare le modifiche
    def save_changes(event):
        updated_data = pd.DataFrame({"RPM": rpm, "Torque_NM": torque})
        save_lut(updated_data, path=file_path)

    # Funzione per salvare con nome
    def save_as(event):
        updated_data = pd.DataFrame({"RPM": rpm, "Torque_NM": torque})
        save_lut(updated_data)

    # Funzione per aggiornare il grafico
    def refresh_plot(event):
        global rpm, torque
        updated_data = pd.DataFrame({"RPM": rpm, "Torque_NM": torque})
        temp_path = os.path.join(os.path.dirname(file_path), "temp_lut.lut")
        save_lut(updated_data, path=temp_path)
        print(f"Grafico aggiornato e salvato temporaneamente in: {temp_path}")
        # Ricarica il file temporaneo
        reloaded_data = reload_temp_lut()
        if reloaded_data is not None:
            rpm = reloaded_data["RPM"].values
            torque = reloaded_data["Torque_NM"].values
            scatter.set_offsets(np.c_[rpm, torque])
            line.set_ydata(torque)
            ax.relim()
            ax.autoscale_view()
            fig.canvas.draw()

    # Aggiunta di un pulsante per salvare
    ax_button_save = plt.axes([0.81, 0.05, 0.15, 0.1])
    button_save = Button(ax_button_save, "Salva")
    button_save.on_clicked(save_changes)

    # Aggiunta di un pulsante per salvare con nome
    ax_button_save_as = plt.axes([0.63, 0.05, 0.15, 0.1])
    button_save_as = Button(ax_button_save_as, "Salva con nome")
    button_save_as.on_clicked(save_as)

    # Aggiunta di un pulsante per aggiornare
    ax_button_refresh = plt.axes([0.45, 0.05, 0.15, 0.1])
    button_refresh = Button(ax_button_refresh, "Aggiorna")
    button_refresh.on_clicked(refresh_plot)

    plt.show()
else:
    print("Impossibile caricare il file LUT.")
