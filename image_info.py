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
    MIN_CANVAS_HEIGHT = 5
    MIN_CANVAS_WIDTH = 5
    img_cache = {}

    def __init__(self, canvas, path=None):
        self.canvas = canvas
        self.path = path
        self.img_original = None
        self.img_scale = 1
        self.sample = None
        self.sample_scale = None
        self.display_image = None
        self.image_id = None

        if path:
            self.load_to_canvas(path)

    def __contains__(self, coord):
        image_x, image_y = self.canvas.coords(self.image_id)
        image_w = self.display_image.width()
        image_h = self.display_image.height()
        return (image_x <= coord[0] <= image_x + image_w) and (image_y <= coord[1] <= image_y + image_h)

    def copy(self):
        img = ImageInfo(self.canvas, self.path)
        img.img_original = self.img_original
        img.img_scale = self.img_scale
        img.sample = self.sample
        img.sample_scale = self.sample_scale

        return img

    def canvas_size(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if h < self.MIN_CANVAS_HEIGHT or w < self.MIN_CANVAS_WIDTH:
            raise RuntimeError(f"Canvas size too small ({w=}, {h=}). Did you draw it?")
        return w, h

    def calc_scale(self, img):
        canvas_w, canvas_h = self.canvas_size()
        if img.width == 0 or img.height == 0:
            return 1.0  # Avoid division by zero
        else:
            scale_w = canvas_w / img.width
            scale_h = canvas_h / img.height
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
        self.image_id = self.canvas.create_image(0, 0,
                                                 image=self.display_image,
                                                 anchor="nw")

    def resize(self, scale):
        """
        Resize the image

        Args:
            scale(float): Zoom scale relative to self.sample image
        """
        self.sample_scale = scale
        new_w = int(self.sample.width * scale)
        new_h = int(self.sample.height * scale)
        resized = self.sample.resize((new_w, new_h), Image.LANCZOS)
        self.display_image = ImageTk.PhotoImage(resized)  # Keep image alife
        self.canvas.itemconfig(self.image_id, image=self.display_image)
