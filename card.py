from shared_lib.img_process import remove_color_and_replace_with_background, write_text_on_image
from PIL import Image


class Card:
    def __init__(self, img=None, filepath=None):
        if filepath is not None:
            # Load the image
            img = Image.open(filepath)
        self.img = img.copy()
        if self.img is None:
            raise ValueError("Image not found or cannot be opened.")
        self.text_boxes = []

    @property
    def width(self):
        return self.img.size[0]

    @property
    def height(self):
        return self.img.size[1]

    def save(self, filepath):
        self.img.save(filepath)

    def add_text_box(self, textbox):
        self.text_boxes.append(textbox)

    def apply_text_boxes(self):
        for box in self.text_boxes:
            self.clean_area(box.color, box.location)
            #blur_rectangle(output_path, box.location, output_path, blur_strength=(5, 5))
            self.img = write_text_on_image(self.img, box.text, box.color, box.location, box.font_path,
                                           box.font_size, align=box.align)
        self.text_boxes = []

    def clean_area(self, color, location):
        def borders(val, min=0, max=255):
            if val < min:
                val = min
            if val > max:
                val = max
            return val

        colors = [(borders(color[0] - delta), borders(color[1] - delta), borders(color[1] - delta)) for delta in [-20, 0, 20, 40]]
        colors = [color]
        for c in colors:
            self.img = remove_color_and_replace_with_background(self.img, c, location)

