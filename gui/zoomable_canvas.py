import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path
from pdf2image import convert_from_path


# TODO: Find right lib for it
def get_suffix(filepath):
    """Get file extension"""
    return str(Path(filepath).suffix).lower()


class ZoomableCanvas(tk.Canvas):
    """
    Canvas extension, allowing image size change

    Note:
        Derived class MUST treat the following fields:
            * self.original_image
            * self.scale
            * self.image_id
    """
    def __init__(self, master, **kwargs):
        """Initialize"""
        kwargs.setdefault("bd", 2)
        kwargs.setdefault("relief", "solid")
        super().__init__(master, **kwargs)

        self.cached_content = {}

        # Load image
        self.original_image = None
        self.scale = 1.0

        # Display image
        self.display_image = None
        self.image_id = None

        # Variables to store drag state
        self.drag = {"x": 0, "y": 0}

        # Bind mouse wheel (Windows / Linux)
        self.bind("<MouseWheel>", self.on_zoom)        # Windows
        self.bind("<Button-4>", self.on_zoom)          # Linux scroll up
        self.bind("<Button-5>", self.on_zoom)          # Linux scroll down
        # Bind drag/drop
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<B1-Motion>", self.on_drag)

        # MacOS uses event.delta as well, but with different scaling
        self.bind("<Configure>", self.on_resize)

    def clear(self):
        self.delete("all")

    def load(self, path):
        """Load image from file"""
        self.clear()

        suffix = get_suffix(path)
        if suffix in (".png", ".jpg", ".jpeg", ".bmp", ".gif"):
            self.load_image(path)
        elif suffix == ".pdf":
            self.load_pdf(path)
        elif suffix in (".txt", ".py", ".md", ".json", ".csv", ".log"):
            self.load_text(path)

        else:
            raise RuntimeError(f"Unsupported file type ({suffix}) for file {path}")

        self.grid()

    def load_text(self, path):
        with open(path, "r") as file:
            text = file.read()
        from shared_lib.text_to_image import text_to_img
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()
        img = text_to_img(text, canvas_width, canvas_height)
        # Display image

        self.original_image = img
        self.display_image = ImageTk.PhotoImage(img)
        self.image_id = self.create_image(0, 0, image=self.display_image, anchor="nw")
        self.grid()

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
        self.original_image = img
        self.scale = self.calc_scale()
        new_w = int(img.width * self.scale)
        new_h = int(img.height * self.scale)
        resized = self.original_image.resize((new_w, new_h), Image.LANCZOS)

        # Display image
        self.display_image = ImageTk.PhotoImage(resized)
        self.image_id = self.create_image(0, 0, image=self.display_image, anchor="nw")
        self.grid()

    def load_image(self, path):
        """Load an image"""
        if path in self.cached_content:
            img = self.cached_content[path]
        else:
            img = Image.open(path)
            self.cached_content[path] = img
        self.original_image = img
        self.scale = self.calc_scale()
        new_w = int(img.width * self.scale)
        new_h = int(img.height * self.scale)
        resized = self.original_image.resize((new_w, new_h), Image.LANCZOS)

        # Display image
        self.display_image = ImageTk.PhotoImage(resized)
        self.image_id = self.create_image(0, 0, image=self.display_image, anchor="nw")
        self.grid()

    def keep_image_in_bounds(self):
        """Ensure the image never leaves the visible canvas area."""
        x, y = self.coords(self.image_id)
        cw, ch = self.winfo_width(), self.winfo_height()
        iw, ih = self.display_image.width(), self.display_image.height()

        # Clamp x, y so that at least the canvas area is filled
        if iw > cw:
            x = min(0, max(x, cw - iw))
        else:
            x = (cw - iw) / 2  # center if smaller

        if ih > ch:
            y = min(0, max(y, ch - ih))
        else:
            y = (ch - ih) / 2

        self.coords(self.image_id, x, y)

    def on_press(self, event):
        """Record where the user clicked"""
        self.drag["x"] = event.x
        self.drag["y"] = event.y

    def restrict_drag(self, dx, dy):
        return dx, dy

    def on_drag(self, event):
        """Compute how far the mouse moved"""
        dx = event.x - self.drag["x"]
        dy = event.y - self.drag["y"]
        self.drag["x"] = event.x
        self.drag["y"] = event.y

        # Move the image
        # TODO:
        #dx, dy = self.restrict_drag(dx, dy)
        self.move(self.image_id, dx, dy)

        # Keep the image within bounds
        #self.keep_image_in_bounds()

    def calc_scale(self,
                   canvas_width=None,
                   canvas_height=None,
                   image_width=None,
                   image_height=None):
        """
        Calculate scale factor so the entire image fits inside the canvas.

        Args:
            canvas_width (int): Width of the canvas
            canvas_height (int): Height of the canvas
            image_width (int): Original image width
            image_height (int): Original image height

        Returns:
            float: Scale factor (≤ 1 if image larger than canvas)
        """

        canvas_width = canvas_width if canvas_width else self.winfo_width()
        canvas_height = canvas_height if canvas_height else self.winfo_height()
        image_width = image_width if image_width else self.original_image.width
        image_height = image_height if image_height else self.original_image.height
        if image_width == 0 or image_height == 0:
            return 1.0  # Avoid division by zero

        if canvas_width == 1:
            canvas_width = self.master.winfo_width()
            canvas_height = self.master.winfo_height()
        scale_w = canvas_width / image_width
        scale_h = canvas_height / image_height
        return min(scale_w, scale_h)
        '''TextBox(character, (15, 3, 70, 8), (20, 20, 20), align="center",
                font_name="times new roman", font_type="bold", font_size=40)'''

    def on_resize(self, event):
        """
        Keep image scaled so it's never smaller than the canvas area.
        Triggered on <Configure> (resize) event.
        """
        if not self.original_image:
            # Nothing shown
            return

        # Get new canvas size
        canvas_w = event.width
        canvas_h = event.height

        # Original image size
        orig_w, orig_h = self.original_image.size

        # Compute minimum scale so image covers canvas completely
        scale_w = canvas_w / orig_w
        scale_h = canvas_h / orig_h
        new_scale = min(scale_w, scale_h)  # ensures image >= canvas in both directions

        # Update only if scale changed significantly (optional optimization)
        if abs(new_scale - self.scale) < 0.01:
            return

        self.scale = new_scale

        self.resize_image()

    def on_zoom(self, event):
        """Increase or decrease image size"""
        if not self.original_image:
            return

        # Determine zoom direction
        if event.num == 5 or event.delta < 0:
            self.scale /= 1.1  # zoom out
        elif event.num == 4 or event.delta > 0:
            self.scale *= 1.1  # zoom in

        # Clamp scale
        self.scale = max(0.1, min(10.0, self.scale))

        # Resize and update image
        self.resize_image()

        # Keep top-left corner fixed
        self.config(scrollregion=self.bbox("all"))

    def resize_image(self):
        """Resize the image"""
        new_w = int(self.original_image.width * self.scale)
        new_h = int(self.original_image.height * self.scale)
        resized = self.original_image.resize((new_w, new_h), Image.LANCZOS)
        self.display_image = ImageTk.PhotoImage(resized)  # Keep image alife
        self.itemconfig(self.image_id, image=self.display_image)
