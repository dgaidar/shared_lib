'''
Convert pdf file to images (one per page)
'''
import tkinter as tk
from tkinter import ttk, StringVar
from shared_lib.history import History
from shared_lib.gui.widget_select_file import WidgetSelectFile
from gui.widget_run import WidgetRun
from PIL import Image, ImageTk
import os
from shared_lib.img_process import pdf_to_png


class WidgetPreviewFolder(tk.Frame):
    path2image = {} # Cache file content

    def __init__(self, parent, **kwargs):
        #kwargs.setdefault("bd", 2)
        #kwargs.setdefault("relief", "solid")    # style: "flat", "raised", "sunken", "groove", "ridge", "solid"
        super().__init__(parent, **kwargs)

        #self.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Frame where icons will go
        self.content_frame = ttk.Frame(scrollable_frame)
        self.content_frame.pack(fill="both", expand=True)

    def load_folder(self, path):
        THUMB_SIZE = (128, 128)  # size of preview thumbnails
        COLUMNS = 2  # how many per row

        # Clear existing thumbnails
        for w in self.content_frame.winfo_children():
            w.destroy()

        thumbs = []
        row = col = 0

        for fname in os.listdir(path):
            fpath = os.path.join(path, fname)

            # Try opening image files only
            try:
                if fpath in self.path2image:
                    img = self.path2image[fpath]
                else:
                    img = Image.open(fpath)
                    self.path2image[fpath] = img
            except Exception:
                continue  # skip non-images

            # Create thumbnail
            img.thumbnail(THUMB_SIZE, Image.LANCZOS)
            thumb = ImageTk.PhotoImage(img)
            thumbs.append(thumb)  # keep a reference!

            # Frame for each image preview
            cell = ttk.Frame(self.content_frame, width=THUMB_SIZE[0] + 20, height=THUMB_SIZE[1] + 40)
            cell.grid(row=row, column=col, padx=10, pady=10)
            cell.grid_propagate(False)

            # Thumbnail label
            lbl = ttk.Label(cell, image=thumb)
            lbl.image = thumb
            lbl.pack()

            # Filename label
            name = f"{fname}  [{img.width}x{img.height}]"
            ttk.Label(cell, text=name, wraplength=THUMB_SIZE[0], justify="center").pack()

            # Click to preview action
            lbl.bind("<Button-1>", lambda e, path=fpath: print("Clicked:", path))

            # Next column / row
            col += 1
            if col >= COLUMNS:
                col = 0
                row += 1

    def run(self):
        pdf_to_png(self.panel_src_folder.get_path(), self.panel_dst_dir.get_path())

