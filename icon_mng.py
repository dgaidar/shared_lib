from pathlib import Path
from PIL import Image, ImageTk


class IconMng:
    path = None
    files = []
    WIDTH = 24
    HEIGHT = 24

    @classmethod
    def set_path(cls, path):
        if not Path(path).is_dir():
            raise RuntimeError(f"Provided icon folder path doesn't exist")
        cls.path = Path(path)
        cls.files = [f for f in cls.path.iterdir() if f.is_file()]

    @classmethod
    def get_available_icons(cls):
        if cls.path is None:
            raise RuntimeError(f"{cls} not initialized. Please call: {cls}.set_path(...)")
        return [f.stem for f in cls.files]

    @classmethod
    def get_img(cls, name):
        if cls.path is None:
            raise RuntimeError(f"{cls} not initialized. Please call: {cls}.set_path(...)")
        names = cls.get_available_icons()
        if name not in names:
            raise RuntimeError(f"Unknown item '{name}'. Available icons are: {names}")
        for f in cls.files:
            if str(f.name).startswith(f"{name}."):
                img = Image.open(f)
                img = img.resize((cls.WIDTH, cls.HEIGHT), Image.LANCZOS)  # precise resize
                icon = ImageTk.PhotoImage(img)
                return icon
        raise RuntimeError(f"Unknown item '{name}'. Available icons are: {cls.files}")