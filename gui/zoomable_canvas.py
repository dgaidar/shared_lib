import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path
from pdf2image import convert_from_path
from shared_lib.image_info import ImageInfo
from shared_lib.image_load import get_suffix


class ZoomableCanvas(tk.Canvas):
    """
    Canvas extension, allowing image size change

    Note:
        Derived class MUST treat the following fields:
            * self.image.img_original
            * self.image.sample_scale
            * self.image.image_id
    """
    ZOOM_MIN = 0.1
    ZOOM_MAX = 3

    def __init__(self, master, **kwargs):
        """Initialize"""
        kwargs.setdefault("bd", 2)
        kwargs.setdefault("relief", "solid")
        super().__init__(master, **kwargs)

        self.cached_content = {}

        # Load image
        self.image = ImageInfo(self)

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
        self.image.load_to_canvas(path)
        self.grid()

    def keep_image_in_bounds(self):
        """Ensure the image never leaves the visible canvas area."""
        x, y = self.coords(self.image.image_id)
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

        self.coords(self.image.image_id, x, y)

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
        self.move(self.image.image_id, dx, dy)

        # Keep the image within bounds
        #self.keep_image_in_bounds()

    def calc_scale(self,
                   canvas_width=None,
                   canvas_height=None,
                   image_width=None,
                   image_height=None,
                   all_visable=False):
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
        image_width = image_width if image_width else self.image.img_original.width
        image_height = image_height if image_height else self.image.img_original.height
        if image_width == 0 or image_height == 0:
            return 1.0  # Avoid division by zero

        if canvas_width == 1:
            canvas_width = self.master.winfo_width()
            canvas_height = self.master.winfo_height()
        scale_w = canvas_width / image_width
        scale_h = canvas_height / image_height

        if all_visable:
            res = max(scale_w, scale_h)
        else:
            res = min(scale_w, scale_h)
        return res

    def on_resize(self, event):
        """
        Keep image scaled so it's never smaller than the canvas area.
        Triggered on <Configure> (resize) event.
        """
        if not self.image.img_original:
            # Nothing shown
            return

        # Get new canvas size
        canvas_w = event.width
        canvas_h = event.height

        # Original image size
        orig_w, orig_h = self.image.img_original.size

        # Compute minimum scale so image covers canvas completely
        scale_w = canvas_w / orig_w
        scale_h = canvas_h / orig_h
        new_scale = min(scale_w, scale_h)  # ensures image >= canvas in both directions

        # Update only if scale changed significantly (optional optimization)
        if abs(new_scale - self.image.sample_scale) < 0.01:
            return

        self.image.resize(new_scale)

    def on_zoom(self, event):
        """Increase or decrease image size"""
        if not self.image.sample:
            return

        # Determine zoom direction
        if event.num == 5 or event.delta < 0:
            scale = self.image.sample_scale / 1.1  # zoom out
        elif event.num == 4 or event.delta > 0:
            scale = self.image.sample_scale * 1.1  # zoom in

        # Clamp scale
        scale = self.apply_limits(scale)

        # Resize and update image
        self.image.resize(scale)

        # Keep top-left corner fixed
        self.config(scrollregion=self.bbox("all"))

    def apply_limits(self, scale):
        """Check that the current scale is inside min/max borders. If not - fix it"""
        if scale < self.ZOOM_MIN:
            return self.ZOOM_MIN
        if scale > self.ZOOM_MAX:
            return self.ZOOM_MAX
        return scale

    def resize_image(self):
        """Resize the image"""
        new_w = int(self.image.img_original.width * self.image.sample_scale)
        new_h = int(self.image.img_original.height * self.image.sample_scale)
        resized = self.image.img_original.resize((new_w, new_h), Image.LANCZOS)
        self.display_image = ImageTk.PhotoImage(resized)  # Keep image alife
        self.itemconfig(self.image.image_id, image=self.display_image)
