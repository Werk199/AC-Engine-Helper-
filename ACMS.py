import numpy as np
import matplotlib.pyplot as plt
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
                # Legge il file riga per riga
                data = []
                for line in file:
                    line = line.strip()  # Rimuove spazi e newline
                    if line:  # Ignora righe vuote
                        input_val, output_val = line.split('|')  # Divide la riga in base al pipe
                        data.append((float(input_val), float(output_val)))  # Converte in float
                return np.array(data)  # Restituisce un array numpy
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare il file LUT: {e}")
            return np.array([])

    def save_lut(self, data):
        """Salva i dati in un file LUT."""
        try:
            with open(self.file_path, 'w') as file:
                for input_val, output_val in data:
                    file.write(f"{int(input_val)}|{int(output_val)}\n")  # Salva nel formato corretto
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
            nonlocal x, y  # Rende x e y accessibili all'interno di questa funzione
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


# Classe per gestire la visualizzazione e modifica dei valori del cambio
class GearboxViewer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.config = configparser.ConfigParser(interpolation=None)  # Disabilita l'interpolazione
        self.edited_values = {}  # Dizionario per memorizzare le modifiche

    def load_drivetrain_ini(self):
        """Carica le sezioni [GEARS], [DIFFERENTIAL], [GEARBOX] dal file drivetrain.ini."""
        try:
            self.config.read(self.file_path)
            # Carica le sezioni (se presenti)
            self.gears = dict(self.config['GEARS']) if 'GEARS' in self.config else {}
            self.differential = dict(self.config['DIFFERENTIAL']) if 'DIFFERENTIAL' in self.config else {}
            self.gearbox = dict(self.config['GEARBOX']) if 'GEARBOX' in self.config else {}
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare il file drivetrain.ini: {e}")
            self.gears, self.differential, self.gearbox = {}, {}, {}

    def display_drivetrain_values(self):
        """Mostra i valori delle sezioni [GEARS], [DIFFERENTIAL], [GEARBOX] in una finestra."""
        self.load_drivetrain_ini()
        if not self.gears and not self.differential and not self.gearbox:
            return

        # Creazione della finestra principale
        self.root = tk.Tk()
        self.root.title("Modifica Drivetrain.ini")

        # Creazione di un notebook per le schede
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        # Aggiungi una scheda per ogni sezione
        if self.gears:
            self.add_section_tab("GEARS", self.gears)
        if self.differential:
            self.add_section_tab("DIFFERENTIAL", self.differential)
        if self.gearbox:
            self.add_section_tab("GEARBOX", self.gearbox)

        # Pulsante per salvare le modifiche
        btn_save = ttk.Button(self.root, text="Salva Modifiche", command=self.save_changes)
        btn_save.pack(pady=10)

        self.root.mainloop()

    def add_section_tab(self, section_name, section_data):
        """Aggiunge una scheda per una sezione specifica."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=section_name)

        # Creazione della Treeview per la sezione
        tree = ttk.Treeview(frame, columns=('Key', 'Value'), show='headings', selectmode='browse')
        tree.heading('Key', text='Chiave')
        tree.heading('Value', text='Valore')
        tree.column('Key', width=150, anchor='w')
        tree.column('Value', width=150, anchor='w')

        # Inserimento dei dati
        for key, value in section_data.items():
            tree.insert('', 'end', values=(key, value))

        tree.pack(expand=True, fill='both')

        # Binding per la modifica delle celle
        tree.bind('<Double-1>', lambda e, t=tree, s=section_name: self.on_double_click(e, t, s))

    def on_double_click(self, event, tree, section_name):
        """Gestisce il doppio click per modificare il valore nella colonna 'Value'."""
        item_id = tree.focus()
        if not item_id:
            return

        column = tree.identify_column(event.x)
        if column == '#2':  # Solo la colonna 'Value' è modificabile
            key, old_value = tree.item(item_id, 'values')
            x, y, width, height = tree.bbox(item_id, column)

            # Creazione di un Entry per la modifica
            entry = tk.Entry(tree)
            entry.insert(0, old_value)
            entry.focus()

            def on_return(event):
                new_value = entry.get()
                tree.set(item_id, column='Value', value=new_value)
                self.edited_values[(section_name, key)] = new_value  # Salva la modifica
                entry.destroy()

            entry.bind("<Return>", on_return)
            entry.bind("<Escape>", lambda e: entry.destroy())
            entry.place(x=x, y=y, width=width, height=height)

    def save_changes(self):
        """Salva le modifiche apportate al file drivetrain.ini."""
        if not self.edited_values:
            messagebox.showinfo("Nessuna Modifica", "Non sono state effettuate modifiche.")
            return

        # Applica le modifiche al config
        for (section, key), new_value in self.edited_values.items():
            if section in self.config:
                self.config[section][key] = new_value

        # Salva il file
        try:
            with open(self.file_path, 'w') as configfile:
                self.config.write(configfile)
            messagebox.showinfo("Successo", "Modifiche salvate correttamente!")
            self.edited_values.clear()  # Resetta le modifiche
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile salvare il file: {e}")


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
        self.notebook.add(self.tab_gearbox, text="Drivetrain.ini")

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
        """Configura la scheda per la modifica del drivetrain.ini."""
        frame = ttk.LabelFrame(self.tab_gearbox, text="Drivetrain.ini")
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Button(frame, text="Carica Drivetrain.ini", command=self.display_drivetrain_values).pack(pady=5)

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

    def display_drivetrain_values(self):
        """Mostra i valori del drivetrain.ini."""
        file_path = filedialog.askopenfilename(filetypes=[("INI files", "*.ini")])
        if file_path:
            gearbox_viewer = GearboxViewer(file_path)
            gearbox_viewer.display_drivetrain_values()


# Avvio dell'applicazione
if __name__ == "__main__":
    root = tk.Tk()
    app = AssettoCorsaManagerApp(root)
    root.mainloop()
