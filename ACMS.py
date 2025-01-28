import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import configparser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Classe per gestire la modifica dei file LUT
class LUTEditor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_lut()

    def load_lut(self):
        """Carica i dati da un file LUT."""
        try:
            with open(self.file_path, 'r') as file:
                return np.loadtxt(file)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare il file LUT: {e}")
            return np.array([])

    def save_lut(self, data):
        """Salva i dati in un file LUT."""
        try:
            with open(self.file_path, 'w') as file:
                np.savetxt(file, data)
            messagebox.showinfo("Successo", "File LUT salvato correttamente.")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile salvare il file LUT: {e}")

    def plot_and_modify_lut(self):
        """Mostra un grafico interattivo per modificare i punti LUT."""
        if self.data.size == 0:
            return

        x, y = self.data[:, 0], self.data[:, 1]
        fig, ax = plt.subplots()
        ax.plot(x, y, 'bo-', label="Curva LUT")
        ax.set_title("Modifica LUT")
        ax.set_xlabel("Input")
        ax.set_ylabel("Output")
        ax.legend()

        # Funzione per catturare i click del mouse e aggiornare i punti
        def onclick(event):
            if event.inaxes is not None:
                new_x, new_y = event.xdata, event.ydata
                x = np.append(x, new_x)
                y = np.append(y, new_y)
                ax.plot(x, y, 'ro-', label="Curva Modificata")
                plt.draw()

        fig.canvas.mpl_connect('button_press_event', onclick)
        plt.show()

        # Salva i dati modificati
        self.save_lut(np.column_stack((x, y)))


# Classe per gestire la modifica del file engine.ini
class EngineEditor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.config = configparser.ConfigParser()

    def load_engine_ini(self):
        """Carica il file engine.ini."""
        try:
            self.config.read(self.file_path)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare il file engine.ini: {e}")

    def add_custom_torque_curve(self, lut_file_path):
        """Aggiunge una curva di torque personalizzata al file engine.ini."""
        if 'ENGINE_DATA' not in self.config:
            self.config['ENGINE_DATA'] = {}
        self.config['ENGINE_DATA']['TORQUE_CURVE'] = lut_file_path

        try:
            with open(self.file_path, 'w') as configfile:
                self.config.write(configfile)
            messagebox.showinfo("Successo", "Curva di torque aggiunta con successo.")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile salvare il file engine.ini: {e}")


# Classe per gestire la visualizzazione dei valori del cambio
class GearboxViewer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.config = configparser.ConfigParser()

    def load_gearbox_values(self):
        """Carica i valori del cambio da un file INI."""
        try:
            self.config.read(self.file_path)
            if 'GEARBOX' in self.config:
                return dict(self.config['GEARBOX'])
            return {}
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare i valori del cambio: {e}")
            return {}

    def display_gearbox_values(self):
        """Mostra i valori del cambio in una finestra."""
        gearbox_values = self.load_gearbox_values()
        if not gearbox_values:
            return

        root = tk.Tk()
        root.title("Valori del Cambio")

        tree = ttk.Treeview(root, columns=('Gear', 'Value'), show='headings')
        tree.heading('Gear', text='Marcia')
        tree.heading('Value', text='Valore')

        for gear, value in gearbox_values.items():
            tree.insert('', 'end', values=(gear, value))

        tree.pack(expand=True, fill='both')
        root.mainloop()


# Interfaccia grafica principale
class AssettoCorsaManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Assetto Corsa Manager")

        self.notebook = ttk.Notebook(root)
        self.tab_lut = ttk.Frame(self.notebook)
        self.tab_engine = ttk.Frame(self.notebook)
        self.tab_gearbox = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_lut, text="Modifica LUT")
        self.notebook.add(self.tab_engine, text="Engine.ini")
        self.notebook.add(self.tab_gearbox, text="Cambio")

        self.notebook.pack(expand=True, fill='both')

        self.setup_lut_tab()
        self.setup_engine_tab()
        self.setup_gearbox_tab()

    def setup_lut_tab(self):
        """Configura la scheda per la modifica LUT."""
        frame = ttk.LabelFrame(self.tab_lut, text="Modifica LUT")
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Button(frame, text="Carica LUT", command=self.load_lut).pack(pady=5)
        ttk.Button(frame, text="Modifica LUT", command=self.modify_lut).pack(pady=5)

    def setup_engine_tab(self):
        """Configura la scheda per la modifica engine.ini."""
        frame = ttk.LabelFrame(self.tab_engine, text="Engine.ini")
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Button(frame, text="Carica Engine.ini", command=self.load_engine_ini).pack(pady=5)
        ttk.Button(frame, text="Aggiungi Curva di Torque", command=self.add_torque_curve).pack(pady=5)

    def setup_gearbox_tab(self):
        """Configura la scheda per la visualizzazione del cambio."""
        frame = ttk.LabelFrame(self.tab_gearbox, text="Valori del Cambio")
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Button(frame, text="Carica Valori del Cambio", command=self.display_gearbox_values).pack(pady=5)

    def load_lut(self):
        """Carica un file LUT."""
        file_path = filedialog.askopenfilename(filetypes=[("LUT files", "*.lut")])
        if file_path:
            self.lut_editor = LUTEditor(file_path)

    def modify_lut(self):
        """Modifica il file LUT caricato."""
        if hasattr(self, 'lut_editor'):
            self.lut_editor.plot_and_modify_lut()
        else:
            messagebox.showwarning("Attenzione", "Nessun file LUT caricato.")

    def load_engine_ini(self):
        """Carica un file engine.ini."""
        file_path = filedialog.askopenfilename(filetypes=[("INI files", "*.ini")])
        if file_path:
            self.engine_editor = EngineEditor(file_path)
            self.engine_editor.load_engine_ini()

    def add_torque_curve(self):
        """Aggiunge una curva di torque personalizzata."""
        if hasattr(self, 'engine_editor'):
            lut_file_path = filedialog.askopenfilename(filetypes=[("LUT files", "*.lut")])
            if lut_file_path:
                self.engine_editor.add_custom_torque_curve(lut_file_path)
        else:
            messagebox.showwarning("Attenzione", "Nessun file engine.ini caricato.")

    def display_gearbox_values(self):
        """Mostra i valori del cambio."""
        file_path = filedialog.askopenfilename(filetypes=[("INI files", "*.ini")])
        if file_path:
            gearbox_viewer = GearboxViewer(file_path)
            gearbox_viewer.display_gearbox_values()


# Avvio dell'applicazione
if __name__ == "__main__":
    root = tk.Tk()
    app = AssettoCorsaManagerApp(root)
    root.mainloop()
