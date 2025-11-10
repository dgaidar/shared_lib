import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
from pdf2image import convert_from_path
from shared_lib.gui.zoomable_canvas import ZoomableCanvas
from pathlib import Path


# TODO: Find right lib for it
def get_suffix(filepath):
    """Get file extension"""
    return str(Path(filepath).suffix).lower()


class WidgetPreview(tk.Frame):
    """Panel displaying file content"""

    def __init__(self, parent, **kwargs):
        """Create a panel with multiple canvases (only one is shown)

        :param parent: ttk.Frame: Parent frame
        """
        kwargs.setdefault("bd", 2)
        kwargs.setdefault("relief", "solid")
        super().__init__(parent, **kwargs)
        self.cached_content = {}

        # Image canvas
        self.canvas_panel = ZoomableCanvas(self, bg="white", bd=2, relief="solid")
        self.canvas_panel.clear = lambda: self.canvas_panel.delete("all")
        self.canvas_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=0, pady=0)

    def load(self, path):
        """Load image from file"""
        self.clear()

        suffix = get_suffix(path)
        if suffix in (".png", ".jpg", ".jpeg", ".bmp", ".gif"):
            self.load_image(path)
        elif suffix == ".pdf":
            self.load_pdf(path)
        else:
            raise RuntimeError(f"Unsupported file type ({suffix}) for file {path}")

        self.canvas_panel.pack(fill="both", expand=True)

    def load_pdf(self, path):
        """Load from PDF file"""
        if path in self.cached_content:
            img = self.cached_content[path]
        else:
            pages = convert_from_path(path, dpi=150, first_page=1, last_page=1)
            if not pages:
                raise RuntimeError(f"PDF {path} appears to be empty.")
            img = pages[0]
            self.cached_content[path] = img
        self.canvas_panel.original_image = img
        self.canvas_panel.scale = self.canvas_panel.calc_scale()
        self.canvas_panel.resize_image()

    def load_image(self, path):
        """Load an image"""
        if path in self.cached_content:
            img = self.cached_content[path]
        else:
            img = Image.open(path)
            self.cached_content[path] = img
        self.canvas_panel.original_image = img
        self.canvas_panel.scale = self.canvas_panel.calc_scale()
        self.canvas_panel.resize_image()

    def clear(self):
        """Delete all data from preview panel"""
        self.filepath = None
        self.canvas_panel.delete("all")
