import os
import shlex, subprocess
import tkinter
from pathlib import Path

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip


class FrameOutputDirectory(ttk.Frame):
    from tkinter.filedialog import askdirectory

    @staticmethod
    def show_directory_dialog() -> str:
        path = FrameOutputDirectory.askdirectory(title="Ablageverzeichnis für digitalisierte Bilder",
                                                 initialdir=".",
                                                 mustexist=False)
        return r'{}'.format(path)

    def __init__(self, master):
        super().__init__(master)

        self.configure(borderwidth=3, relief=SOLID)
        self.directory_label = ttk.Label(self, text="Ausgabeverzeichnis", font=("Helvetica", 16))
        self.directory_label.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="ew")
        self.directory_path = ttk.Entry(self, font=("Helvetica", 16), takefocus=0)
        self.directory_path.insert(0, os.getcwd())
        self.directory_path.configure(state=ttk.READONLY)
        self.directory_path.grid(row=0, column=1, pady=(10, 10), sticky="ew")

        s = ttk.Style()
        s.configure('beck-view-gui.TButton', font=('Helvetica', 16))
        self.directory_button = ttk.Button(self,
                                           text="Auswählen",
                                           style="beck-view-gui.TButton",
                                           command=self.directory_button_callback)
        self.directory_button.grid(row=0, column=2, padx=(10, 10))
        ToolTip(self.directory_button,
                text="Öffnet den Dialog zur Auswahl des Verzeichnisses in dem die digitalisierten Bilder abgelegt "
                     "werden.",
                bootstyle="INFO, INVERSE")

    def directory_button_callback(self):
        path = FrameOutputDirectory.show_directory_dialog()
        self.directory_path.configure(state=ttk.NORMAL)
        text = self.directory_path.get()
        if len(path) > 0:
            self.directory_path.delete(0, len(text))
            self.directory_path.insert(index=0, string=path)
        self.directory_path.configure(state=ttk.READONLY)


class TechnicalAttributes(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(borderwidth=3, relief=SOLID)
        row = 0
        self.spule_counter_label = ttk.Label(self,
                                             font=("Helvetica", 16),
                                             text="Maximale Anzahl Bilder")
        self.spule_counter_label.grid(row=row, column=0, padx=(10, 0), pady=(10, 10), sticky="ew")
        self.spule_counter_values = [
            "3600 (15-m-Kassette)",
            "7200 (30-m-Kassette)",
            "14400 (60-m-Kassette)",
            "21800 (90-m-Kassette)",
            "43600 (180-m-Kassette)",
            "60000 (250-m-Kassette)"
        ]
        self.spule_counter = ttk.Combobox(self,
                                          font=("Helvetica", 16),
                                          values=self.spule_counter_values,
                                          state=ttk.READONLY)

        self.spule_counter.grid(row=row, column=1, padx=(10, 10), pady=(10, 10), sticky="ew")
        self.spule_counter.current(1)
        ToolTip(self.spule_counter,
                text="Notbremse - beendet die Digitalisierung spätestens bei Erreichen der ausgewählten Anzahl Bilder.",
                bootstyle="INFO, INVERSE")

        row += 1
        self.batch_label = ttk.Label(self, font=("Helvetica", 16), text="Parallele Anzahl Bilder")
        self.batch_label.grid(row=row, column=0, padx=(10, 0), pady=(10, 10), sticky="ew")
        self.batch = ttk.Spinbox(self, font=("Helvetica", 16), from_=1, to=100, state=ttk.READONLY)
        self.batch.grid(row=row, column=1, padx=(10, 10), pady=(10, 10), sticky="ew")
        self.batch.set(8)
        ToolTip(self.batch,
                text="Anzahl Bilder die in einem `Paket`parallel verarbeitet werden. Beeinflusst die "
                     "Verarbeitungs-geschwindigkeit.\nWertebereich 1 bis 99.",
                bootstyle="INFO, INVERSE")


class Preferences(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(borderwidth=3, relief=SOLID)

        self.device_label = ttk.Label(self, font=("Helvetica", 16), text="Gerätenummer der Kamera")
        self.device_label.grid(row=0, column=0, padx=(10, 0), sticky="ew")
        self.device = ttk.Spinbox(self, font=("Helvetica", 16), from_=0, to=9, state=ttk.READONLY)
        self.device.grid(row=0, column=1, padx=(0, 10), pady=(10, 10), sticky="ew")
        self.device.set(0)
        ToolTip(self.device,
                text="Vom System vergebene Geräte-Id.\nZulässiger Wertebereich ist 0 bis 9.",
                bootstyle="INFO, INVERSE")

        s = ttk.Style()
        s.configure('beck-view-gui.TCheckbutton', font=('Helvetica', 16))
        s.map('beck-view-gui.TCheckbutton',
              font=[('focus', ('Helvetica', 16, 'italic'))])

        self.monitor = tkinter.StringVar()
        self.monitor_checkbutton = ttk.Checkbutton(self, text="Monitor-Fenster anzeigen",
                                                   onvalue=True, offvalue=False,
                                                   variable=self.monitor,
                                                   style='beck-view-gui.TCheckbutton'
                                                   )

        self.monitor_checkbutton.grid(row=1, column=0, padx=(10, 0), pady=(10, 10), sticky="ew")
        ToolTip(self.monitor_checkbutton,
                text="Vorschaufenster öffnen, in dem die digitalisierten Bilder angezeigt werden.\nReduziert die "
                     "Digitalisierungs-geschwindigkeit.",
                bootstyle="INFO, INVERSE")
        self.monitor.set("True")


class MainMenu(ttk.Menu):
    def __init__(self, master):
        super().__init__(master)
        self.file_menu = ttk.Menu(self, tearoff=1)
        self.file_menu.add_command(label="Neues Projekt")
        self.file_menu.add_command(label="Letzte Projekte")
        self.file_menu.add_command(label="Projekt schließen")
        self.file_menu.add_command(label="Alle Projekte schließen")
        self.file_menu.add_command(label="Projekt umbenennen")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Beenden", command=master.destroy)
        self.add_cascade(label="Datei", menu=self.file_menu, underline=0)

        self.window_menu = tkinter.Menu(self, tearoff=0)
        self.window_menu.add_command(label="Minimieren")
        self.window_menu.add_command(label="Vollbild")
        self.add_cascade(label="Fenster", menu=self.window_menu, underline=0)


class GroupLayout(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # Create other GUI elements
        self.preferences = Preferences(self)
        self.preferences.grid_rowconfigure(0, weight=1)
        self.preferences.grid_columnconfigure(1, weight=1)
        self.preferences.grid_columnconfigure(0, weight=1)
        self.preferences.grid(row=0, column=0, padx=10, pady=10, sticky="ewn")

        self.directory_dialog = FrameOutputDirectory(self)
        self.directory_dialog.grid_rowconfigure(0, weight=1)
        self.directory_dialog.grid_columnconfigure(0, weight=0)
        self.directory_dialog.grid_columnconfigure(1, weight=1)
        self.directory_dialog.grid_columnconfigure(2, weight=0)
        self.directory_dialog.grid(row=1, column=0, padx=10, pady=10, sticky="ewn")

        self.technical_attributes = TechnicalAttributes(self)
        self.technical_attributes.grid_rowconfigure(0, weight=1)
        self.technical_attributes.grid_columnconfigure(1, weight=1)
        self.technical_attributes.grid_columnconfigure(0, weight=1)
        self.technical_attributes.grid(row=2, column=0, padx=10, pady=10, sticky="ewn")


class SplashScreen(tkinter.Toplevel):
    def __init__(self):
        super().__init__()

        self.overrideredirect(True)  # Remove window decorations

        # Calculate the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate the coordinates to center the splash screen
        x_coordinate = (screen_width - 1024) // 2
        y_coordinate = (screen_height - 1024) // 2

        # Set the position and size of the splash screen
        self.geometry(f"1024x1024+{x_coordinate}+{y_coordinate}")

        # Load splash image
        self.splash_image = ttk.PhotoImage(file="beck-view-digitize.png")

        splash_label = ttk.Label(self, image=self.splash_image)
        splash_label.pack()

        # After a delay, close the splash screen
        self.after(5000, self.destroy)


class App(ttk.Window):
    def __init__(self):
        super().__init__(title="Beck-View", minsize=[640, 480], themename="superhero")

        # Show splash screen
        SplashScreen()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create main menu
        self.menubar = MainMenu(self)
        self.config(menu=self.menubar)

        self.group_layout = GroupLayout(self)
        self.group_layout.grid_rowconfigure(0, weight=1)
        self.group_layout.grid_columnconfigure(0, weight=1)
        self.group_layout.grid(row=0, column=0, padx=0, pady=0, sticky="ewn")

        self.group_layout.preferences.device.focus_set()

        s = ttk.Style()
        s.configure('beck-view-gui.TButton', font=('Helvetica', 16))

        self.button = ttk.Button(self, text="Start Digitalisierung", style='beck-view-gui.TButton',
                                 command=self.button_callback)
        self.button.grid(row=3, column=0, padx=10, pady=10, sticky="ewn")

    def button_callback(self):
        filepath = Path.home().joinpath('PycharmProjects', 'beck-view-digitalize', 'beck-view-digitize')
        args = [str(filepath)]
        # Spawn subprocess with configured command line options
        if self.group_layout.preferences.device.get() != '0':
            args.append(f"-d {self.group_layout.preferences.device.get()}")

        if self.group_layout.preferences.monitor.get():
            args.append("-s")

        args.append("-o")
        args.append(f"{self.group_layout.directory_dialog.directory_path.get()}")

        emergency_stop = self.group_layout.technical_attributes.spule_counter.get().split(" ")[0]

        if emergency_stop != self.group_layout.technical_attributes.spule_counter_values[1].split(" ")[0]:
            args.append(f"-m {emergency_stop}")

        if self.group_layout.technical_attributes.batch.get() != '8':
            args.append(f"-c {self.group_layout.technical_attributes.batch.get()}")

        try:
            print(f"Subprocess started: {args}")
            p = subprocess.call(args)
            print(f"Subprocess finished {p.returncode}")
        except Exception as e:
            print(f"Error starting 'beck-view-digitize': {e}")
        finally:
            print("FINALLY")
        exit(0)


if __name__ == '__main__':
    app = App()
    app.mainloop()
