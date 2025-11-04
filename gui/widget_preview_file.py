import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
from pdf2image import convert_from_path
from gui.zoomable_canvas import ZoomableCanvas
from pathlib import Path


# TODO: Find right lib for it
def get_suffix(filepath):
    """Get file extension"""
    return str(Path(filepath).suffix).lower()


class WidgetPreview(tk.Frame):
    """Panel displaying file content"""

    def __init__(self, parent, label=None, **kwargs):
        """Create a panel with multiple canvases (only one is shown)

        :param parent: ttk.Frame: Parent frame
        :param label: str: The label of this frame (if provided)
        """
        super().__init__(parent, **kwargs)
        self.cached_content = {}

        # Panel Label
        self.label = tk.Label(self, text=label)
        if label:
            self.label.pack(side=tk.TOP, anchor='w')

        # Text will be displayed here
        self.text_panel = ScrolledText(self, wrap=tk.WORD)
        self.text_panel.clear = lambda : self.text_panel.delete('1.0', tk.END)
        self.text_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Image/PDF canvas (initially hidden)
        self.canvas_panel = ZoomableCanvas(self, bg="white")
        self.canvas_panel.clear = lambda: self.canvas_panel.delete("all")
        self.canvas_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.active_widget = self.text_panel
        self.inactive_widget = self.canvas_panel
        self.inactive_widget.pack_forget()  # hidden until needed

    def hide(self):
        """Hide the preview"""
        self.canvas_panel.pack_forget()
        self.text_panel.pack_forget()
        self.pack_forget()

    def show(self):
        """Display preview"""
        self.hide()
        self.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=0, pady=0)
        self.active_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=0, pady=0)

    def load(self, path):
        """Load image from file"""
        self.clear()
        self.active_widget.pack_forget()
        self.inactive_widget.pack_forget()

        suffix = get_suffix(path)
        if suffix in (".png", ".jpg", ".jpeg", ".bmp", ".gif"):
            self.load_image(path)
        elif suffix == ".pdf":
            self.load_pdf(path)
        elif suffix in (".txt", ".py", ".md", ".json", ".csv", ".log"):
            self.load_text(path)
        else:
            raise RuntimeError(f"Unsupported file type ({suffix}) for file {path}")

        self.active_widget.pack(fill="both", expand=True)

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
        resized = self.canvas_panel.resize_image()

        # Display image
        self.canvas_panel.display_image = ImageTk.PhotoImage(resized)
        self.canvas_panel.image_id = self.canvas_panel.create_image(0, 0, image=self.canvas_panel.display_image, anchor="nw")
        self.canvas_panel.pack(fill=tk.BOTH, expand=True)

        self.active_widget = self.canvas_panel
        self.inactive_widget = self.text_panel

    def load_text(self, path):
        """Load from text file"""
        if path not in self.cached_content:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            self.cached_content[path] = text

        self.text_panel.insert("1.0", text)
        self.active_widget = self.text_panel
        self.inactive_widget = self.canvas_panel

    def load_image(self, path):
        """Load an image"""
        if path in self.cached_content:
            img = self.cached_content[path]
        else:
            img = Image.open(path)
            self.cached_content[path] = img
        self.canvas_panel.original_image = img
        self.canvas_panel.scale = self.canvas_panel.calc_scale()
        resized = self.canvas_panel.resize_image()

        # Display image
        self.canvas_panel.display_image = ImageTk.PhotoImage(resized)
        self.canvas_panel.image_id = self.canvas_panel.create_image(0, 0, image=self.canvas_panel.display_image, anchor="nw")
        self.canvas_panel.pack(fill=tk.BOTH, expand=True)

    def clear(self):
        """Delete all data from preview panel"""
        self.filepath = None
        self.text_panel.delete("1.0", tk.END)
        self.canvas_panel.delete("all")
