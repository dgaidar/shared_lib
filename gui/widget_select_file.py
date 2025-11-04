import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
from gui.button_open_folder import ButtonOpenFolder
from lib.error import Error

class WidgetSelectFile(tk.Frame):

    def __init__(self, parent, is_folder, history, init_from_history=True, text=None):
        """Compound widget for file/folder selection"""

        # Main Panel ###########################################################
        super().__init__(parent,
                         bd=2,  # border width
                         relief="solid"  # style: "flat", "raised", "sunken", "groove", "ridge", "solid"
                         )
        self.parent = parent
        self.history = history
        self.is_folder = is_folder
        #self.columnconfigure(1, weight=1)

        # Source File Selection ################################################
        if text is None:
            text = "Folder:" if is_folder else "File:"
        self.label = tk.Label(self, text=text)
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # ComboBox #############################################################
        # Use a StringVar to store the combobox value (path)
        self.var_path = tk.StringVar()
        self.var_folder = tk.StringVar()
        self.var_path.trace_add("write", self.set_folder_var)

        self.combobox = ttk.Combobox(self, textvariable=self.var_path,
                                     values=self.history.values)
        if init_from_history:
            if self.history.values:
                self.combobox.set(self.history.values[-1])
        self.combobox.grid(row=0, column=1, padx=5, pady=(5, 0), sticky="ew")

        # Select from system GUI ###############################################
        self.btn_browse = tk.Button(self, text="Browse", command=self.browse)
        self.btn_browse.grid(row=0, column=2, padx=5, pady=5)

        # Open Folder Icon #####################################################
        self.btn_open = ButtonOpenFolder(self, self.var_folder)
        self.btn_open.grid(row=0, column=3, padx=5, pady=2)

    def set_folder_var(self, *args):
        filepath = self.var_path.get()
        if self.is_folder:
            self.var_folder.set(filepath)
        else:
            parent = Path(filepath).parent
            if not parent.exists():
                Error.show(f"Path '{parent}' doesn't exist")
                return
            if not parent.is_dir():
                Error.show(f"Path '{parent}' is not a folder")
                return
            self.var_folder.set(str(parent))

    def get_path(self):
        """Get widget's value"""
        return self.var_path.get()

    def browse(self):
        """Find file or folder by system's browser"""
        if self.is_folder:
            path = filedialog.askdirectory(title="Select a Folder")
        else:
            path = filedialog.askopenfilename(title="Select a File")
        if path:
            self.history.update(path)
            self.combobox["values"] = self.history.values
            self.combobox.set(path)
