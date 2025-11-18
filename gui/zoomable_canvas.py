import tkinter as tk
from PIL import Image, ImageTk
from shared_lib.image_info import ImageInfo
from shared_lib.action_control import CanvasAction


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

        self.action = CanvasAction(self, move=True, scroll=True, resize=True)

        # Load image
        self.image = ImageInfo(self)

    def get_images(self, event):
        return [self.image]

    def clear(self):
        self.delete("all")

    def load(self, path):
        """Load image from file"""
        self.clear()
        self.image.load_to_canvas(path)
        self.grid()
