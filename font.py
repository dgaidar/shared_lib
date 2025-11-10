from PIL import ImageFont
from pathlib import Path


"""
class Font:
    def __init__(self, font_name=None, font_type="", font_size=None):
        if font_size is None:
            raise ValueError('"font_size" is not provided')
        self.font = FontManager.get_font(font_name, font_type, font_size)
        self.size = font_size
"""


class FontManager:
    supported_types = ['', 'bold', 'italic', 'bold italic']
    supported_fonts = ['times new roman']

    @classmethod
    def get_font_path(cls, font_name, font_type=""):
        if font_name not in cls.supported_fonts:
            raise ValueError(f'Unknown font: "{font_name}". Supported fonts are: {cls.supported_fonts}')
        if font_type not in cls.supported_types:
            raise ValueError(f'Unknown font type: "{font_type}". Supported font types are: {cls.supported_types}')
        filename = font_name
        if len(font_type):
            filename = f'{filename} {font_type}'
        font_path = Path(f'shared_lib/fonts/{font_name}/') / f'{filename}.ttf'

        return font_path

    @classmethod
    def get_font(cls, font_name, font_size, font_type=""):
        font_path = cls.get_font_path(font_name, font_type)
        font = ImageFont.truetype(font_path, font_size)
        return font
