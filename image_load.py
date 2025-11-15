from PIL import Image
from pathlib import Path
from shared_lib.text_to_image import text_to_img
from pdf2image import convert_from_path


def get_suffix(filepath):
    """Get file extension"""
    return str(Path(filepath).suffix).lower()


def load(path):
    """Load image from file"""
    suffix = get_suffix(path)
    if suffix in (".png", ".jpg", ".jpeg", ".bmp", ".gif"):
        return load_image(path)
    elif suffix == ".pdf":
        return load_pdf(path)
    elif suffix in (".txt", ".py", ".md", ".json", ".csv", ".log"):
        return load_text(path)

    raise RuntimeError(f"Unsupported file type ({suffix}) for file {path}")


def load_text(path, width, height):
    with open(path, "r") as file:
        text = file.read()
    img = text_to_img(text, width, height)
    return img


def load_pdf(path):
    """Load from PDF file"""
    pages = convert_from_path(path, dpi=150, first_page=1, last_page=1)
    if not pages:
        raise RuntimeError(f"PDF {path} appears to be empty.")
    img = pages[0]
    return img


def load_image(path):
    """Load an image"""
    img = Image.open(path)
    return img
