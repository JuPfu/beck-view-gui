import asyncio
import os
import platform
import signal
import subprocess
import time
import tkinter
from asyncio import Task
from pathlib import Path

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.tooltip import ToolTip

beck_view_font = ("Helvetica", 14)


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
        self.directory_label = ttk.Label(self, text="Ausgabeverzeichnis", font=beck_view_font)
        self.directory_label.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="ew")
        self.directory_path = ttk.Entry(self, font=beck_view_font, takefocus=0)
        self.directory_path.insert(0, os.getcwd())
        self.directory_path.configure(state=ttk.READONLY)
        self.directory_path.grid(row=0, column=1, pady=(10, 10), sticky="ew")

        s = ttk.Style()
        s.configure('beck-view-gui.TButton', font=beck_view_font)
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

        self.batch_label = ttk.Label(self, font=beck_view_font,
                                     text="Anzahl Bilder, die jedem Prozess übergeben werden")
        self.batch_label.grid(row=row, column=0, padx=(10, 0), pady=(10, 10), sticky="ew")
        self.batch = ttk.Spinbox(self, font=beck_view_font, from_=1, to=100, state=ttk.READONLY)
        self.batch.grid(row=row, column=1, padx=(10, 10), pady=(10, 10), sticky="ew")
        self.batch.set(10)
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

        # increase font size for Listbox of Combobox
        list_font = ttk.font.Font(family="Helvetica", size=14)
        self.master.option_add("*TCombobox*Listbox*Font", list_font)

        self.logo = ttk.PhotoImage(file="beck-view-logo.png")
        self.logo_label = ttk.Label(self, image=self.logo)
        self.logo_label.grid(row=0, column=0, rowspan=3, padx=(10, 0), pady=(0, 0), sticky="ew")

        self.panel = ttk.Frame(self, borderwidth=3)
        self.panel.grid(row=0, column=1, rowspan=2, columnspan=4, padx=(0, 0), pady=(0, 0), sticky="ewns")

        self.device_label = ttk.Label(self.panel, font=beck_view_font, text="Gerätenummer der Kamera")
        self.device_label.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="ew")
        self.device = ttk.Spinbox(self.panel, font=beck_view_font, from_=0, to=9, state=ttk.READONLY)
        self.device.grid(row=0, column=1, padx=(0, 10), pady=(10, 10), sticky="ew")
        self.device.set(0)
        ToolTip(self.device,
                text="Vom System vergebene Geräte-Id.\nZulässiger Wertebereich ist 0 bis 9.",
                bootstyle="INFO, INVERSE")

        self.film_resolution_values = [
            "1600 x 1200",
            "1920 x 1080",
            "2048 x 1536",
            "2592 x 1944",
            "3840 x 2160",
        ]

        self.film_resolution_label = ttk.Label(self.panel, font=beck_view_font, text="Auflösung")
        self.film_resolution_label.grid(row=1, column=0, padx=(10, 10), pady=(10, 10), sticky="ew")
        self.film_resolution = ttk.Combobox(self.panel,
                                            font=beck_view_font,
                                            values=self.film_resolution_values,
                                            state=ttk.READONLY)
        self.film_resolution.grid(row=1, column=1, padx=(0, 10), pady=(10, 10), sticky="ew")
        self.film_resolution.current(1)
        ToolTip(self.film_resolution,
                text="Auflösung in horizontaler und vertikaler Richtung.",
                bootstyle="INFO, INVERSE")

        self.frame_counter_label = ttk.Label(self.panel,
                                             font=beck_view_font,
                                             text="Maximale Anzahl Bilder")
        self.frame_counter_label.grid(row=2, column=0, padx=(10, 10), pady=(10, 10), sticky="ew")
        self.frame_counter_values = [
            "3600 (15-m-Kassette)",
            "7200 (30-m-Kassette)",
            "14400 (60-m-Kassette)",
            "21800 (90-m-Kassette)",
            "43600 (180-m-Kassette)",
            "60000 (250-m-Kassette)"
        ]

        self.frame_counter = ttk.Combobox(self.panel,
                                          font=beck_view_font,
                                          values=self.frame_counter_values,
                                          state=ttk.READONLY)

        self.frame_counter.grid(row=2, column=1, padx=(0, 10), pady=(5, 5), sticky="ew")
        self.frame_counter.current(3)
        ToolTip(self.frame_counter,
                text="Notbremse - beendet die Digitalisierung spätestens bei Erreichen der ausgewählten Anzahl Bilder.",
                bootstyle="INFO, INVERSE")

        s = ttk.Style()
        s.configure('beck-view-gui.TCheckbutton', font=beck_view_font)
        s.map('beck-view-gui.TCheckbutton',
              font=[('focus', ('Helvetica', 14, 'italic'))],
              background=[('focus', 'white')],
              )

        self.exposure_bracketing = tkinter.BooleanVar()
        self.exposure_bracketing.set(False)

        self.exposure_bracketing_checkbutton = ttk.Checkbutton(self.panel, text="Belichtungsreihe aktivieren",
                                                               onvalue=True, offvalue=False,
                                                               variable=self.exposure_bracketing,
                                                               padding="5  10",
                                                               style='beck-view-gui.TCheckbutton'
                                                               )
        self.exposure_bracketing_checkbutton.grid(row=0, column=2, padx=(30, 0), pady=(10, 10), sticky="ew")
        ToolTip(self.exposure_bracketing_checkbutton,
                text="Belichtungsreihe aktivieren (Exposure Bracketing)",
                bootstyle="INFO, INVERSE")

        if os.name == 'nt':
            self.display_menu = tkinter.BooleanVar()
            self.display_menu.set(True)

            self.display_menu_checkbutton = ttk.Checkbutton(self.panel, text="Einstellungsfenster anzeigen ",
                                                            onvalue=True, offvalue=False,
                                                            variable=self.display_menu,
                                                            padding="5  10",
                                                            style='beck-view-gui.TCheckbutton'
                                                            )
            self.display_menu_checkbutton.grid(row=2, column=2, padx=(30, 0), pady=(10, 10), sticky="ew")
            ToolTip(self.display_menu_checkbutton,
                    text="Unter Windows separaten Dialog mit den Konfigurationsparametern der Kamera anzeigen (Direct-Show). Ansonsten wird unter Windows das MS Media Foundation API verwendet.",
                    bootstyle="INFO, INVERSE")


class SubprocessOutput(ttk.LabelFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(borderwidth=3, text="Ausgabe `Beck-View-Digitize`", relief=SOLID)

        # Create ScrolledText widget for displaying subprocess output
        self.text_output = ScrolledText(self, height=10, font=beck_view_font, wrap=WORD, autohide=True, takefocus=FALSE)
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
        self.window_menu.add_command(label="Normal", command=self.normal)
        self.window_menu.add_command(label="Vollbild", command=self.maximize)
        self.window_menu.add_command(label="Minimiert", command=self.minimize)
        self.add_cascade(label="Fenster", menu=self.window_menu, underline=0)

    def maximize(self):
        app.state("zoomed")

    def normal(self):
        app.state("normal")

    def minimize(self):
        app.state("iconic")


class GroupLayout(ttk.Frame):
    def __init__(self, master, windows: bool):
        super().__init__(master)

        self.windows = windows

        # Create other GUI elements
        self.preferences = Preferences(self)
        self.preferences.grid_columnconfigure(0, weight=0)
        self.preferences.grid_columnconfigure(1, weight=0)
        self.preferences.grid_columnconfigure(2, weight=0)
        self.preferences.grid_columnconfigure(3, weight=2)
        self.preferences.grid(row=0, column=0, columnspan=3, padx=(10, 10), pady=(10, 10), sticky=EW)

        self.output_directory = FrameOutputDirectory(self)
        self.output_directory.grid_columnconfigure(0, weight=0)
        self.output_directory.grid_columnconfigure(1, weight=1)
        self.output_directory.grid_columnconfigure(2, weight=0)
        self.output_directory.grid(row=1, column=0, columnspan=3, padx=(10, 10), pady=(10, 10), sticky=EW)

        self.technical_attributes = TechnicalAttributes(self)
        self.technical_attributes.grid(row=2, column=0, columnspan=3, padx=(10, 10), pady=(10, 10), sticky=EW)

        self.subprocess_output = SubprocessOutput(self)
        self.subprocess_output.grid(row=3, column=0, columnspan=3, padx=(10, 10), pady=(10, 10), sticky=NSEW)

        self.start_button = ttk.Button(self,
                                       text="Beck-View-Digitize starten",
                                       style="beck-view-gui.TButton",
                                       command=self.start_digitization)
        self.start_button.grid(row=4, column=0, columnspan=1, padx=(10, 10), pady=(10, 10), sticky=EW)

        self.stop_button = ttk.Button(self,
                                      text="Beck-View-Digitize stoppen",
                                      style="beck-view-gui.TButton",
                                      command=self.stop_digitization)
        self.stop_button.grid(row=4, column=1, columnspan=1, padx=(10, 10), pady=(10, 10), sticky=EW)

        # Configure grid weights
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create asyncio event loop
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Store reference to subprocess
        self.process = None
        self.output_task: Task

    async def read_subprocess_output(self, process: asyncio.subprocess.Process):
        # Asynchronously read subprocess output
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            self.subprocess_output.text_output.insert(tkinter.END, line.decode())
            self.subprocess_output.text_output.see(tkinter.END)

    def start_digitization(self):
        self.subprocess_output.text_output.insert(tkinter.END, "Beck-View-GUI - Starte Digitalisierung...\n")

        async def run_digitization():
            filepath = Path.home().joinpath('PycharmProjects',
                                            'beck-view-digitalize',
                                            'digitize.cmd' if self.windows else 'beck-view-digitize')
            width_height = self.preferences.film_resolution.get().split(" x ")
            width = width_height[0]
            height = width_height[1]

            command = [
                str(filepath),
                f"--device={self.preferences.device.get()}",
                f"--width={width}",
                f"--height={height}",
                f"--max-count={self.preferences.frame_counter.get().split()[0]}",
                f"--output-path={self.output_directory.directory_path.get()}",
                f"--chunk-size={self.technical_attributes.batch.get()}"
            ]
            if self.preferences.exposure_bracketing.get():
                command.append("--bracketing")

            if os.name == 'nt' and self.preferences.display_menu.get():
                command.append("--show-menu")

            self.subprocess_output.text_output.insert(tkinter.END,
                                                      f"Beck-View-GUI - Beck-View-Digitize wird mit folgenden Parametern gestartet: {command}\n")
            try:
                if self.windows:
                    self.process = await asyncio.create_subprocess_exec(
                        *command,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        creationflags=subprocess.REALTIME_PRIORITY_CLASS | subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
                    )
                else:
                    self.process = await asyncio.create_subprocess_exec(
                        *command,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        preexec_fn=os.setpgrp
                    )

                # Start reading subprocess output asynchronously
                self.output_task = self.loop.create_task(self.read_subprocess_output(self.process))

                # Wait for the process to finish
                await self.process.wait()
                await self.output_task

                self.subprocess_output.text_output.insert(tkinter.END,
                                                          f"Beck-View-GUI - Beck-View-Digitize wurde mit Return-Code '{self.process.returncode}' beendet. \n")
                self.process = None

            except Exception as e:
                self.subprocess_output.text_output.insert(tkinter.END,
                                                          f"Beck-View-GUI - Error starting subprocess: {e}\n")
            finally:
                self.subprocess_output.text_output.see(tkinter.END)

        self.loop.create_task(run_digitization())

    def stop_digitization(self):
        if self.process:
            self.subprocess_output.text_output.insert(tkinter.END, "Beck-View-GUI - Stoppe Beck-View-Digitize ...\n")
            try:
                if not self.output_task.cancelled():
                    self.subprocess_output.text_output.insert(tkinter.END,
                                                              "Beck-View-GUI - Beende Ausgabe von Nachrichten gesendet von Beck-View-Digitize ...\n")
                    self.output_task.cancel()

                if self.windows:
                    self.process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    self.process.terminate()

                time.sleep(1)

                self.subprocess_output.text_output.insert(tkinter.END, "Beck-View-GUI - Beck-View-Digitize gestoppt!\n")
                self.process = None
            except Exception as e:
                self.subprocess_output.text_output.insert(tkinter.END,
                                                          f"Beck-View-GUI - Fehler beim Stoppen von Beck-View-Digitize: {e}\n")
            finally:
                self.subprocess_output.text_output.see(tkinter.END)
        else:
            self.subprocess_output.text_output.insert(tkinter.END,
                                                      "Beck-View-GUI - Kein laufender Prozess 'Beck-View-Digitize' gefunden!\n")
            self.subprocess_output.text_output.see(tkinter.END)


class Application(ttk.Window):
    def __init__(self):
        super().__init__(themename="morph")

        self.windows = platform.system() == "Windows"

        self.minsize(width=1280, height=800)
        self.geometry("1280x800")
        self.title("Beck View Digitalisierer")
        self.option_add("*tearOff", False)

        self.iconbitmap("beck-view-gui.ico")

        self.menu = MainMenu(self)
        self.config(menu=self.menu)

        self.layout = GroupLayout(self, self.windows)
        self.layout.pack(fill=BOTH, expand=YES)

        # Integrate asyncio event loop with Tkinter
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.loop = self.layout.loop
        self.update_loop()

    def update_loop(self):
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()
        self.after(100, self.update_loop)

    def on_closing(self):
        self.loop.call_soon(self.loop.stop)
        self.loop.close()
        self.destroy()


if __name__ == "__main__":
    app = Application()
    app.mainloop()
