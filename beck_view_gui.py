"""Beck-View GUI - Oberfläche zum Starten und Stoppen von Beck-View-Digitize.

tkinter/ttk mit optionalem Theme aus dem Paket ttkthemes (pip install ttkthemes).
Der Subprozess wird in einem Hintergrund-Thread gelesen, die Ausgabe gelangt
über eine Queue in die GUI.
"""

import platform
import queue
import signal
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

try:
    from ttkthemes import ThemedTk  # pip install ttkthemes
except ImportError:  # GUI läuft auch ohne das Paket (dann mit Standard-Theme)
    ThemedTk = None

# Theme aus ttkthemes, z. B. "arc", "equilux" (dunkel), "breeze", "adapta",
# "yaru", "plastik", "radiance", "clearlooks", "black"
THEME_NAME = "blue"

APP_DIR = Path(__file__).resolve().parent
BECK_VIEW_FONT = ("Helvetica", 14)
IS_WINDOWS = platform.system() == "Windows"

DIGITIZE_PATH = Path.home().joinpath(
    "PycharmProjects",
    "beck-view-digitalize",
    "digitize.cmd" if IS_WINDOWS else "beck-view-digitize",
)
DEFAULT_OUTPUT_DIR = Path("~", "Filme").expanduser()


def find_asset(name: str) -> Path | None:
    """Sucht eine Ressource (Logo, Icon) neben dem Skript und im aktuellen Arbeitsverzeichnis."""
    for folder in (APP_DIR, Path.cwd()):
        candidate = folder / name
        if candidate.is_file():
            return candidate
    return None


BaseWindow = ThemedTk if ThemedTk is not None else tk.Tk


def themed_text_colors() -> dict:
    """Farben für klassische tk-Widgets (Text), damit sie zum aktiven ttk-Theme passen."""
    style = ttk.Style()
    background = style.lookup("TEntry", "fieldbackground") or style.lookup("TFrame", "background") or "white"
    foreground = style.lookup("TEntry", "foreground") or style.lookup("TLabel", "foreground") or "black"
    return {"background": background, "foreground": foreground, "insertbackground": foreground}


class ToolTip:
    """Einfacher Tooltip für beliebige Widgets."""

    def __init__(self, widget: tk.Widget, text: str):
        self.widget = widget
        self.text = text
        self.tip: tk.Toplevel | None = None
        widget.bind("<Enter>", self.show, add="+")
        widget.bind("<Leave>", self.hide, add="+")
        widget.bind("<ButtonPress>", self.hide, add="+")

    def show(self, _event=None):
        if self.tip:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        # Außen ein Rahmen (1 px Rand), innen ein Label mit Abstand zum Rand.
        # Der Abstand wird in Millimetern angegeben und so von Tk passend zur
        # Bildschirmauflösung umgerechnet (feste Pixelwerte wirken auf
        # hochauflösenden Displays kaum sichtbar).
        pad_x = round(self.widget.winfo_fpixels("4m"))
        pad_y = round(self.widget.winfo_fpixels("2.5m"))
        border = tk.Frame(self.tip, background="black", padx=1, pady=1)
        border.pack()
        tk.Label(border, text=self.text, justify="left", background="#ffffe0",
                 foreground="black", font=("Helvetica", 11), wraplength=420,
                 borderwidth=0).pack(padx=0, pady=0, ipadx=pad_x, ipady=pad_y)

    def hide(self, _event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


class FrameOutputDirectory(ttk.Labelframe):
    def __init__(self, master):
        super().__init__(master, text="Zielordner für digitalisierte Bilder",
                         borderwidth=3, relief=tk.SOLID)

        self.path_var = tk.StringVar(value=str(DEFAULT_OUTPUT_DIR))

        self.directory_label = ttk.Label(self, text="Ausgabeverzeichnis", font=BECK_VIEW_FONT)
        self.directory_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.EW)

        self.directory_path = ttk.Entry(self, font=BECK_VIEW_FONT, takefocus=False,
                                        textvariable=self.path_var, state="readonly")
        self.directory_path.grid(row=0, column=1, pady=10, sticky=tk.EW)

        self.directory_button = ttk.Button(self, text="Auswählen",
                                           style="beck-view-gui.TButton",
                                           command=self.directory_button_callback)
        self.directory_button.grid(row=0, column=2, padx=10)
        ToolTip(self.directory_button,
                "Öffnet den Dialog zur Auswahl des Zielordners, in dem die "
                "digitalisierten Bilder abgelegt werden.")

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

    def directory_button_callback(self):
        initial = self.path_var.get()
        if not Path(initial).is_dir():
            initial = str(DEFAULT_OUTPUT_DIR if DEFAULT_OUTPUT_DIR.is_dir() else Path.home())
        path = filedialog.askdirectory(title="Ablageverzeichnis für digitalisierte Bilder",
                                       initialdir=initial, mustexist=False)
        if path:  # Abbruch des Dialogs lässt den bisherigen Wert unverändert
            self.path_var.set(str(Path(path)))

    def get(self) -> str:
        return self.path_var.get()


class TechnicalAttributes(ttk.Labelframe):
    def __init__(self, master):
        super().__init__(master, text="Performance-Tuning", borderwidth=3, relief=tk.SOLID)

        self.batch_var = tk.IntVar(value=5)

        self.batch_label = ttk.Label(self, font=BECK_VIEW_FONT,
                                     text="Anzahl Bilder, die jedem Prozess übergeben werden")
        self.batch_label.grid(row=0, column=0, padx=(10, 0), pady=10, sticky=tk.EW)

        self.batch = ttk.Spinbox(self, font=BECK_VIEW_FONT, from_=1, to=99,
                                 textvariable=self.batch_var, state="readonly")
        self.batch.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)
        ToolTip(self.batch,
                "Anzahl Bilder, die in einem `Paket` parallel verarbeitet werden. "
                "Beeinflusst die Verarbeitungsgeschwindigkeit.\nWertebereich 1 bis 99.")

        self.grid_columnconfigure(2, weight=1)

    def get(self) -> str:
        return str(self.batch_var.get())


class Preferences(ttk.Labelframe):
    FILM_RESOLUTIONS = [
        "1600 x 1200",
        "1920 x 1080",
        "2048 x 1536",
        "2592 x 1944",
        "3840 x 2160",
    ]
    FRAME_COUNTS = [
        "3600 (15-m-Kassette)",
        "7200 (30-m-Kassette)",
        "14400 (60-m-Kassette)",
        "21800 (90-m-Kassette)",
        "43600 (180-m-Kassette)",
        "60000 (250-m-Kassette)",
    ]

    def __init__(self, master):
        super().__init__(master, text="Einstellungen", borderwidth=3, relief=tk.SOLID)

        # Logo oben links (fehlt die Datei, läuft die GUI trotzdem)
        self.logo = None
        logo_file = find_asset("beck-view-logo.png")
        if logo_file:
            self.logo = tk.PhotoImage(file=str(logo_file))  # Referenz halten, sonst wird das Bild gelöscht
            self.logo_label = ttk.Label(self, image=self.logo)
            self.logo_label.grid(row=0, column=0, rowspan=3, padx=(10, 0), pady=(0, 0), sticky=tk.EW)
        else:
            print("Logo 'beck-view-logo.png' nicht gefunden "
                  f"(gesucht in {APP_DIR} und {Path.cwd()})", file=sys.stderr)

        self.panel = ttk.Frame(self, borderwidth=3)
        self.panel.grid(row=0, column=1, rowspan=2, columnspan=4, sticky=tk.NSEW)

        # Gerätenummer
        self.device_var = tk.IntVar(value=0)
        ttk.Label(self.panel, font=BECK_VIEW_FONT, text="Gerätenummer der Kamera").grid(
            row=0, column=0, padx=10, pady=10, sticky=tk.EW)
        self.device = ttk.Spinbox(self.panel, font=BECK_VIEW_FONT, from_=0, to=9, wrap=True,
                                  textvariable=self.device_var, state="readonly")
        self.device.grid(row=0, column=1, padx=(0, 10), pady=10, sticky=tk.EW)
        ToolTip(self.device, "Vom System vergebene Geräte-Id.\nZulässiger Wertebereich ist 0 bis 9.")

        # Auflösung
        ttk.Label(self.panel, font=BECK_VIEW_FONT, text="Auflösung").grid(
            row=1, column=0, padx=10, pady=10, sticky=tk.EW)
        self.film_resolution = ttk.Combobox(self.panel, font=BECK_VIEW_FONT,
                                            values=self.FILM_RESOLUTIONS, state="readonly")
        self.film_resolution.grid(row=1, column=1, padx=(0, 10), pady=10, sticky=tk.EW)
        self.film_resolution.current(1)
        ToolTip(self.film_resolution, "Auflösung in horizontaler und vertikaler Richtung.")

        # Maximale Bildanzahl
        ttk.Label(self.panel, font=BECK_VIEW_FONT, text="Maximale Anzahl Bilder").grid(
            row=2, column=0, padx=10, pady=10, sticky=tk.EW)
        self.frame_counter = ttk.Combobox(self.panel, font=BECK_VIEW_FONT,
                                          values=self.FRAME_COUNTS, state="readonly")
        self.frame_counter.grid(row=2, column=1, padx=(0, 10), pady=5, sticky=tk.EW)
        self.frame_counter.current(3)
        ToolTip(self.frame_counter,
                "Notbremse - beendet die Digitalisierung spätestens bei Erreichen "
                "der ausgewählten Anzahl Bilder.")

        # Belichtungsreihe
        self.exposure_bracketing = tk.BooleanVar(value=False)
        self.exposure_bracketing_checkbutton = ttk.Checkbutton(
            self.panel, text="Belichtungsreihe aktivieren (experimentel)",
            onvalue=True, offvalue=False, variable=self.exposure_bracketing,
            padding="5 10", style="beck-view-gui.TCheckbutton")
        self.exposure_bracketing_checkbutton.grid(row=0, column=2, padx=(30, 0), pady=10, sticky=tk.EW)
        ToolTip(self.exposure_bracketing_checkbutton,
                "Belichtungsreihe aktivieren (Exposure Bracketing) - in Arbeit")

        # Nur unter Windows: DirectShow-Einstellungsdialog
        self.display_menu = tk.BooleanVar(value=True)
        if IS_WINDOWS:
            self.display_menu_checkbutton = ttk.Checkbutton(
                self.panel, text="Einstellungsfenster anzeigen",
                onvalue=True, offvalue=False, variable=self.display_menu,
                padding="5 10", style="beck-view-gui.TCheckbutton")
            self.display_menu_checkbutton.grid(row=2, column=2, padx=(30, 0), pady=10, sticky=tk.EW)
            ToolTip(self.display_menu_checkbutton,
                    "Unter Windows separaten Dialog mit den Konfigurationsparametern der "
                    "Kamera anzeigen (DirectShow). Ansonsten wird unter Windows das "
                    "MS Media Foundation API verwendet.")

        for col, weight in enumerate((0, 0, 0, 2)):
            self.grid_columnconfigure(col, weight=weight)


class SubprocessOutput(ttk.Labelframe):
    def __init__(self, master):
        super().__init__(master, text="Ausgabe `Beck-View-Digitize`", borderwidth=3, relief=tk.SOLID)

        self.text_output = ScrolledText(self, height=10, font=BECK_VIEW_FONT, wrap=tk.WORD,
                                        takefocus=False, state="disabled",
                                        **themed_text_colors())
        self.text_output.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def append(self, text: str):
        self.text_output.configure(state="normal")
        self.text_output.insert(tk.END, text)
        self.text_output.see(tk.END)
        self.text_output.configure(state="disabled")


class MainMenu(tk.Menu):
    def __init__(self, app: "Application"):
        super().__init__(app)
        self.app = app

        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(label="Neues Projekt")
        file_menu.add_command(label="Letzte Projekte")
        file_menu.add_command(label="Projekt schließen")
        file_menu.add_command(label="Alle Projekte schließen")
        file_menu.add_command(label="Projekt umbenennen")
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=app.on_closing)
        self.add_cascade(label="Datei", menu=file_menu, underline=0)

        window_menu = tk.Menu(self, tearoff=False)
        window_menu.add_command(label="Normal", command=self.normal)
        window_menu.add_command(label="Vollbild", command=self.maximize)
        window_menu.add_command(label="Minimiert", command=lambda: self.app.iconify())
        self.add_cascade(label="Fenster", menu=window_menu, underline=0)

    def maximize(self):
        try:
            self.app.state("zoomed")  # Windows, macOS
        except tk.TclError:
            self.app.attributes("-zoomed", True)  # Linux (X11)

    def normal(self):
        try:
            self.app.state("normal")
            self.app.attributes("-zoomed", False)
        except tk.TclError:
            pass


class GroupLayout(ttk.Frame):
    MAX_LINES_PER_TICK = 200

    def __init__(self, master):
        super().__init__(master)

        self.preferences = Preferences(self)
        self.preferences.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky=tk.EW)

        self.output_directory = FrameOutputDirectory(self)
        self.output_directory.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=tk.EW)

        self.technical_attributes = TechnicalAttributes(self)
        self.technical_attributes.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky=tk.EW)

        self.subprocess_output = SubprocessOutput(self)
        self.subprocess_output.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky=tk.NSEW)

        self.start_button = ttk.Button(self, text="Beck-View-Digitize starten",
                                       style="beck-view-gui.TButton",
                                       command=self.start_digitization)
        self.start_button.grid(row=4, column=0, padx=10, pady=10, sticky=tk.EW)

        self.stop_button = ttk.Button(self, text="Beck-View-Digitize stoppen",
                                      style="beck-view-gui.TButton",
                                      command=self.stop_digitization,
                                      state="disabled")
        self.stop_button.grid(row=4, column=1, padx=10, pady=10, sticky=tk.EW)

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.process: subprocess.Popen | None = None
        self.output_queue: queue.Queue = queue.Queue()

    # ------------------------------------------------------------------ helpers
    def log(self, text: str):
        self.subprocess_output.append(text)

    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def _set_running_state(self, running: bool):
        self.start_button.configure(state="disabled" if running else "normal")
        self.stop_button.configure(state="normal" if running else "disabled")

    def build_command(self) -> list[str]:
        width, height = self.preferences.film_resolution.get().split(" x ")
        command = [
            str(DIGITIZE_PATH),
            f"--device={self.preferences.device_var.get()}",
            f"--width={width}",
            f"--height={height}",
            f"--max-count={self.preferences.frame_counter.get().split()[0]}",
            f"--output-path={self.output_directory.get()}",
            f"--chunk-size={self.technical_attributes.get()}",
            "--gui",
        ]
        if self.preferences.exposure_bracketing.get():
            command.append("--bracketing")
        if IS_WINDOWS and self.preferences.display_menu.get():
            command.append("--show-menu")
        return command

    # ------------------------------------------------------------------ start
    def start_digitization(self):
        if self.is_running():
            self.log("Beck-View-GUI - Beck-View-Digitize läuft bereits!\n")
            return

        self.log("Beck-View-GUI - Starte Digitalisierung...\n")

        if not DIGITIZE_PATH.exists():
            self.log(f"Beck-View-GUI - Programm nicht gefunden: {DIGITIZE_PATH}\n")
            return

        command = self.build_command()
        self.log("Beck-View-GUI - Beck-View-Digitize wird mit folgenden Parametern "
                 f"gestartet: {command}\n")

        popen_kwargs: dict = dict(
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # stderr in denselben Strom, sonst Pipe-Stau
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        if IS_WINDOWS:
            popen_kwargs["creationflags"] = (subprocess.HIGH_PRIORITY_CLASS
                                             | subprocess.CREATE_NEW_PROCESS_GROUP
                                             | subprocess.CREATE_NO_WINDOW)
        else:
            popen_kwargs["start_new_session"] = True

        try:
            self.process = subprocess.Popen(command, **popen_kwargs)
        except OSError as e:
            self.log(f"Beck-View-GUI - Fehler beim Starten des Subprozesses: {e}\n")
            self.process = None
            return

        self.output_queue = queue.Queue()
        threading.Thread(target=self._reader_thread,
                         args=(self.process, self.output_queue),
                         daemon=True).start()

        self._set_running_state(True)
        self.after(50, self._poll_output)

    @staticmethod
    def _reader_thread(process: subprocess.Popen, out_queue: queue.Queue):
        """Läuft im Hintergrund: liest zeilenweise und meldet am Ende den Return-Code."""
        try:
            assert process.stdout is not None
            for line in process.stdout:
                out_queue.put(("line", line))
        finally:
            out_queue.put(("done", process.wait()))

    def _poll_output(self):
        """Läuft im GUI-Thread: leert die Queue und aktualisiert das Textfeld."""
        finished = False
        for _ in range(self.MAX_LINES_PER_TICK):
            try:
                kind, payload = self.output_queue.get_nowait()
            except queue.Empty:
                break
            if kind == "line":
                self.log(payload)
            else:
                self.log(f"Beck-View-GUI - Beck-View-Digitize wurde mit Return-Code "
                         f"'{payload}' beendet.\n")
                finished = True
                break

        if finished:
            self.process = None
            self._set_running_state(False)
        else:
            self.after(50, self._poll_output)

    # ------------------------------------------------------------------- stop
    def stop_digitization(self):
        if not self.is_running():
            self.log("Beck-View-GUI - Kein laufender Prozess 'Beck-View-Digitize' gefunden!\n")
            return

        self.log("Beck-View-GUI - Stoppe Beck-View-Digitize ...\n")
        self.terminate_process()

    def terminate_process(self):
        process = self.process
        if process is None or process.poll() is not None:
            return
        try:
            if IS_WINDOWS:
                process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                process.terminate()
        except OSError as e:
            self.log(f"Beck-View-GUI - Fehler beim Stoppen von Beck-View-Digitize: {e}\n")
            return
        # Reagiert der Prozess nicht, nach 5 s hart beenden
        self.after(5000, self._force_kill, process)

    def _force_kill(self, process: subprocess.Popen):
        if process.poll() is None:
            self.log("Beck-View-GUI - Prozess reagiert nicht, wird beendet (kill).\n")
            try:
                process.kill()
            except OSError:
                pass


class Application(BaseWindow):
    def __init__(self):
        if ThemedTk is not None:
            # themebg=True: Fensterhintergrund passt zum gewählten Theme (wichtig bei dunklen Themes)
            super().__init__(theme=THEME_NAME, themebg=True)
        else:
            print("ttkthemes nicht installiert - verwende Standard-Theme.", file=sys.stderr)
            super().__init__()

        self.title("Beck View Digitalisierer")
        self.minsize(width=1280, height=800)
        self.geometry("1280x800")
        self.option_add("*tearOff", False)
        # größere Schrift in der Auswahlliste der Comboboxen
        self.option_add("*TCombobox*Listbox.font", BECK_VIEW_FONT)

        self._setup_styles()  # eigene Styles erst nach dem Theme setzen
        self._setup_icon()

        self.menu = MainMenu(self)
        self.config(menu=self.menu)

        self.layout = GroupLayout(self)
        self.layout.pack(fill="both", expand=True)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    @staticmethod
    def _setup_styles():
        style = ttk.Style()
        style.configure("beck-view-gui.TButton", font=BECK_VIEW_FONT)
        style.configure("beck-view-gui.TCheckbutton", font=BECK_VIEW_FONT)

    def _setup_icon(self):
        try:
            if sys.platform.startswith("win"):
                icon_file = find_asset("beck-view-gui.ico")
                if icon_file:
                    self.iconbitmap(str(icon_file))
            else:
                icon_file = find_asset("beck-view-logo.png")
                if icon_file:
                    self._icon = tk.PhotoImage(file=str(icon_file))
                    self.iconphoto(True, self._icon)
        except tk.TclError:
            pass  # Icon fehlt oder wird nicht unterstützt - nicht kritisch

    def on_closing(self):
        if self.layout.is_running():
            if not messagebox.askokcancel(
                    "Beenden",
                    "Beck-View-Digitize läuft noch.\nProzess stoppen und Programm beenden?",
                    parent=self):
                return
            self.layout.terminate_process()
        self.destroy()


if __name__ == "__main__":
    Application().mainloop()
