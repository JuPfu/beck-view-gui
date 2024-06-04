import os
import subprocess
import tkinter
from pathlib import Path
from tkinter.font import Font
from typing import Any

import ttkbootstrap as ttk
from ttkbootstrap import Checkbutton, Style, Frame, Label
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.tooltip import ToolTip


class FrameOutputDirectory(ttk.LabelFrame):
    from tkinter.filedialog import askdirectory

    @staticmethod
    def show_directory_dialog() -> str:
        path = FrameOutputDirectory.askdirectory(title="Ablageverzeichnis für digitalisierte Bilder",
                                                 initialdir=".",
                                                 mustexist=False)
        return r'{}'.format(path)

    def __init__(self, master):
        super().__init__(master)

        self.configure(borderwidth=3, text="Zielordner für digitalisierte Bilder", relief=SOLID)
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
                text="Öffnet den Dialog zur Auswahl des Zielordners in dem die digitalisierten Bilder abgelegt "
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


class TechnicalAttributes(ttk.LabelFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(borderwidth=3, text="Performance-Tuning", relief=SOLID)
        row = 0

        self.batch_label = ttk.Label(self, font=("Helvetica", 16), text="Parallele Anzahl Bilder")
        self.batch_label.grid(row=row, column=0, padx=(10, 0), pady=(10, 10), sticky="ew")
        self.batch = ttk.Spinbox(self, font=("Helvetica", 16), from_=1, to=100, state=ttk.READONLY)
        self.batch.grid(row=row, column=1, padx=(10, 10), pady=(10, 10), sticky="ew")
        self.batch.set(8)
        ToolTip(self.batch,
                text="Anzahl Bilder die in einem `Paket`parallel verarbeitet werden. Beeinflusst die "
                     "Verarbeitungs-geschwindigkeit.\nWertebereich 1 bis 99.",
                bootstyle="INFO, INVERSE")

        self.panel = ttk.Frame(self, borderwidth=0)
        self.panel.grid(row=row, column=2, rowspan=2, padx=(10, 10), pady=(10, 10), sticky="ewns")


class Preferences(ttk.LabelFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(borderwidth=3, text="Einstellungen", relief=SOLID)

        self.logo = ttk.PhotoImage(file="beck-view-logo.png")
        self.logo_label = ttk.Label(self, image=self.logo)
        self.logo_label.grid(row=0, column=0, rowspan=3, padx=(10, 0), pady=(10, 10), sticky="ew")

        self.device_label = ttk.Label(self, font=("Helvetica", 16), text="Gerätenummer der Kamera")
        self.device_label.grid(row=0, column=1, padx=(10, 10), pady=(10, 10), sticky="ew")
        self.device = ttk.Spinbox(self, font=("Helvetica", 16), from_=0, to=9, state=ttk.READONLY)
        self.device.grid(row=0, column=2, padx=(0, 10), pady=(10, 10), sticky="ew")
        self.device.set(0)
        ToolTip(self.device,
                text="Vom System vergebene Geräte-Id.\nZulässiger Wertebereich ist 0 bis 9.",
                bootstyle="INFO, INVERSE")

        self.frame_counter_label = ttk.Label(self,
                                             font=("Helvetica", 16),
                                             text="Maximale Anzahl Bilder")
        self.frame_counter_label.grid(row=1, column=1, padx=(10, 10), pady=(10, 10), sticky="ew")
        self.frame_counter_values = [
            "3600 (15-m-Kassette)",
            "7200 (30-m-Kassette)",
            "14400 (60-m-Kassette)",
            "21800 (90-m-Kassette)",
            "43600 (180-m-Kassette)",
            "60000 (250-m-Kassette)"
        ]
        self.frame_counter = ttk.Combobox(self,
                                          font=("Helvetica", 16),
                                          values=self.frame_counter_values,
                                          state=ttk.READONLY)

        self.frame_counter.grid(row=1, column=2, padx=(0, 10), pady=(10, 10), sticky="ew")
        self.frame_counter.current(1)
        ToolTip(self.frame_counter,
                text="Notbremse - beendet die Digitalisierung spätestens bei Erreichen der ausgewählten Anzahl Bilder.",
                bootstyle="INFO, INVERSE")

        s = ttk.Style()
        s.configure('beck-view-gui.TCheckbutton', font=('Helvetica', 16))
        s.map('beck-view-gui.TCheckbutton',
              font=[('focus', ('Helvetica', 16, 'italic'))])

        self.monitor = tkinter.BooleanVar()
        self.monitor.set(False)

        self.monitor_checkbutton = ttk.Checkbutton(self, text="Monitor-Fenster anzeigen",
                                                   onvalue=True, offvalue=False,
                                                   variable=self.monitor,
                                                   style='beck-view-gui.TCheckbutton'
                                                   )
        self.monitor_checkbutton.grid(row=2, column=1, padx=(10, 0), pady=(15, 10), sticky="ew")
        ToolTip(self.monitor_checkbutton,
                text="Vorschaufenster öffnen, in dem die digitalisierten Bilder angezeigt werden.\nReduziert die "
                     "Digitalisierungs-geschwindigkeit.",
                bootstyle="INFO, INVERSE")

        self.panel = ttk.Frame(self, borderwidth=0)
        self.panel.grid(row=0, column=3, rowspan=3, padx=(10, 10), pady=(10, 10), sticky="ewns")


class SubprocessOutput(ttk.LabelFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(borderwidth=3, text="Ausgabe `Beck-View-Digitize`", relief=SOLID)

        # Create ScrolledText widget for displaying subprocess output
        self.text_output = ScrolledText(self, height=10, font=("Helvetica", 14), wrap=WORD, autohide=True)
        self.text_output.grid(row=0, column=0, rowspan=10, padx=10, pady=10, sticky=NSEW)

        # Configure grid to make the text_output widget expand
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


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
        self.preferences.grid_columnconfigure(0, weight=0)
        self.preferences.grid_columnconfigure(1, weight=1)
        self.preferences.grid_columnconfigure(2, weight=1)
        self.preferences.grid_columnconfigure(3, weight=2)
        self.preferences.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.directory_dialog = FrameOutputDirectory(self)
        self.directory_dialog.grid_rowconfigure(0, weight=1)
        self.directory_dialog.grid_columnconfigure(0, weight=0)
        self.directory_dialog.grid_columnconfigure(1, weight=1)
        self.directory_dialog.grid_columnconfigure(2, weight=0)
        self.directory_dialog.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.technical_attributes = TechnicalAttributes(self)
        self.technical_attributes.grid_rowconfigure(0, weight=1)
        self.technical_attributes.grid_columnconfigure(0, weight=1)
        self.technical_attributes.grid_columnconfigure(1, weight=1)
        self.technical_attributes.grid_columnconfigure(2, weight=2)
        self.technical_attributes.grid_columnconfigure(3, weight=2)
        self.technical_attributes.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.subprocess_output = SubprocessOutput(self)
        self.subprocess_output.grid(row=3, column=0, padx=10, pady=10, sticky=NSEW)

        # Configure grid weights
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)


class SplashScreen(ttk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Beck-View")

        # self.overrideredirect(True)
        self.resizable(False, False)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x_coordinate = int((screen_width / 2) - (1024 / 2))
        y_coordinate = int((screen_height / 2) - (1024 / 2))

        # Set the position of the window to the center of the screen
        self.geometry(f"1024x1024+{x_coordinate}+{y_coordinate}")

        # Load splash image
        self.splash_image = ttk.PhotoImage(file="beck-view-digitize.png")

        splash_label = ttk.Label(self, image=self.splash_image)
        splash_label.pack()

        # After a delay, close the splash screen
        self.after(5000, self.destroy)


class App(ttk.Window):
    def __init__(self):
        super().__init__(title="Beck-View", minsize=[800, 640], themename="superhero")

        # Show splash screen
        SplashScreen()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create main menu
        self.menubar = MainMenu(self)
        self.config(menu=self.menubar)

        self.group_layout = GroupLayout(self)
        self.group_layout.grid(row=0, column=0, padx=0, pady=0, sticky=NSEW)

        s = ttk.Style()
        s.configure('beck-view-gui.TButton', font=('Helvetica', 16))

        self.button = ttk.Button(self, text="Start Digitalisierung", style='beck-view-gui.TButton',
                                 command=self.button_callback)
        self.button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    def button_callback(self):
        filepath = Path.home().joinpath('PycharmProjects', 'beck-view-digitalize', 'beck-view-digitize')
        args = [str(filepath)]  # path to executable

        # Spawn subprocess with configured command line options
        if self.group_layout.preferences.device.get() != '0':
            args.append("--device")
            args.append(f"{self.group_layout.preferences.device.get()}")

        emergency_stop = self.group_layout.preferences.frame_counter.get().split(" ")[0]
        args.append("--max-count")
        args.append(f"{emergency_stop}")

        if self.group_layout.preferences.monitor.get():
            args.append("--show_monitor")

        args.append("--output-path")
        args.append(f"{self.group_layout.directory_dialog.directory_path.get()}")

        if self.group_layout.technical_attributes.batch.get() != '8':
            args.append("--chunk-size")
            args.append(f"{self.group_layout.technical_attributes.batch.get()}")

        try:
            if self.button.cget('text') == "Start Digitalisierung":

                toast = ToastNotification(
                    title="Beck-View-GUI",
                    message="Die Digitalisierung wird gestartet",
                    duration=3000,
                )
                toast.show_toast()

                print(f"Subprocess started: {args}")
                self.button.configure(text="Stop", style='beck-view-gui.TButton')
                self.button.configure(bootstyle="danger")  # Change button color to red

                # Start the subprocess with stdout and stderr redirected to pipes
                self.p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                # Start reading subprocess output
                self.read_subprocess_output()
            else:
                # If button text is "Stop", kill the subprocess
                self.p.kill()
                self.button.configure(text="Start Digitalisierung", style='beck-view-gui.TButton')
                self.button.configure(bootstyle="primary")  # Change button color back to default
        except Exception as e:
            print(f"Error starting 'beck-view-digitize': {e}")

    def read_subprocess_output(self):
        """Reads the subprocess output and updates the Text widget."""
        try:
            output = self.p.stdout.readline()
            if output:
                self.group_layout.subprocess_output.text_output.insert(END, output)
                self.group_layout.subprocess_output.text_output.see(END)

            error = self.p.stderr.readline()
            if error:
                self.group_layout.subprocess_output.text_output.insert(END, error, "stderr")
                self.group_layout.subprocess_output.text_output.see(END)

            # Continue reading output
            if self.p.poll() is None:
                self.after(500, self.read_subprocess_output)
            # else:
            #     #  Subprocess finished
            #     self.button.configure(text="Start Digitalisierung", style='beck-view-gui.TButton')
            #     self.button.configure(bootstyle="primary")  # Change button color back to default
        except Exception as e:
            self.group_layout.subprocess_output.text_output.insert(END, f"Error reading subprocess output: {e}\n",
                                                                   "stderr")
            self.group_layout.subprocess_output.text_output.see(END)


if __name__ == '__main__':
    app = App()
    app.mainloop()
