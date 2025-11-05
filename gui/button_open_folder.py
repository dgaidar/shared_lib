import tkinter as tk
from PIL import Image, ImageTk
import os
import platform
import subprocess
from shared_lib.gui.error import Error


def get_icon_open_folder():
    """Get 'Open Folder' icon"""
    ICON_OPEN_FOLDER_PATH = "shared_lib/icons/OpenFolder.png"
    # Load and resize
    img = Image.open(ICON_OPEN_FOLDER_PATH)
    img = img.resize((24, 24), Image.LANCZOS)  # precise resize
    icon = ImageTk.PhotoImage(img)
    return icon


class ButtonOpenFolder(tk.Button):
    """Small button that opens in a browser the folder associated with the provided var"""
    def __init__(self, master, var, **kwargs):
        """Initializing"""
        self.icon = get_icon_open_folder()
        super().__init__(master, image=self.icon, command=self.open_folder, **kwargs)
        self.var = var

    def open_folder(self):
        """
        Open a folder in the system's file explorer (File Explorer, Finder, or Nautilus).
        Works on Windows, macOS, and Linux.
        """
        try:
            path = self.var.get()
            if not os.path.exists(path):
                Error.show(f"Path {path} doesn't exist")
                return
            if not os.path.isdir(path):
                Error.show(f"Path {path} is not  folder")
                return
            system = platform.system()

            if system == "Windows":
                os.startfile(path)  # native and simplest

            elif system == "Darwin":  # macOS
                subprocess.Popen(["open", path])

            elif system == "Linux":
                # Try a few common file managers
                for fm in ("xdg-open", "nautilus", "dolphin", "thunar", "nemo", "pcmanfm"):
                    if subprocess.call(["which", fm], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                        subprocess.Popen([fm, path])
                        break
                else:
                    raise RuntimeError("No file manager found (xdg-open, nautilus, etc.)")

            else:
                raise RuntimeError(f"Unsupported OS: {system}")

        except Exception as e:
            Error.show(f"⚠️ Could not open folder {path}:\n{e}")
