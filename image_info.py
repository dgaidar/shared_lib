from shared_lib.image_load import load
from PIL import Image, ImageTk


class FileContentHash:
    content = {}    # FilePath -> FileContent dict

    @classmethod
    def __contains__(cls, path):
        return path in cls.content

    @classmethod
    def get(cls, path):
        return cls.content[path]

    @classmethod
    def sel(cls, path, img):
        cls.content[path] = img


class ImageInfo:
    img_cache = {}
    def __init__(self, canvas, path=None):
        self.canvas = canvas
        self.img_original = None
        self.img_scale = 1
        self.sample = None
        self.sample_scale = None
        self.display_image = None
        self.image_id = None

        if path:
            self.load_to_canvas(path)

    def canvas_size(self):
        MIN_HEIGHT = MIN_WIDTH = 5
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if h < MIN_HEIGHT or w < MIN_WIDTH:
            raise RuntimeError(f"Canvas size too small ({w=}, {h=}). Did you draw it?")
        return w, h

    def calc_scale(self, img):
        canvas_w, canvas_h = self.canvas_size()
        img_w, img_h = img.width, img.width
        if img_w == 0 or img_h == 0:
            return 1.0  # Avoid division by zero
        else:
            scale_w = canvas_w / img_w
            scale_h = canvas_h / img_h
            return min(scale_w, scale_h)

    def load_to_canvas(self, path):
        """Load from file and resize according to canvas"""
        self.path = path
        if path in self.img_cache:
            img = self.img_cache[path]
        else:
            img = load(path)
            self.img_cache[path] = img

        self.img_original = img
        self.img_scale = self.calc_scale(img)
        new_w = int(img.width * self.img_scale)
        new_h = int(img.height * self.img_scale)
        self.sample = self.img_original.resize((new_w, new_h), Image.LANCZOS)
        self.sample_scale = 1

        # Display image
        self.display_image = ImageTk.PhotoImage(self.sample)
        self.image_id = self.canvas.create_image(0, 0, image=self.display_image, anchor="nw")

    def resize(self, scale):
        """Resize the image"""
        self.sample_scale = scale
        new_w = int(self.sample.width * scale)
        new_h = int(self.sample.height * scale)
        resized = self.sample.resize((new_w, new_h), Image.LANCZOS)
        self.display_image = ImageTk.PhotoImage(resized)  # Keep image alife
        self.canvas.itemconfig(self.image_id, image=self.display_image)
