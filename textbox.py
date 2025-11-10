from PIL import Image, ImageDraw, ImageFont
from .font import FontManager


# Split the text into lines to fit within the specified width
def wrap_text(text, font, max_width):
    """Wrap text based on the maximum width without needing the draw object."""
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        # Check the width of the current line with the new word added
        #word_width = font.getsize(word)[0]
        #line_width = font.getsize(' '.join(current_line + [word]))[0]
        #word_width = font.getbbox(word)[2]  # Get the width of the word
        line_width = font.getbbox(' '.join(current_line + [word]))[2]  # Get the width of the line

        if (line_width <= max_width) or len(current_line) == 0:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]

    # Add the last line
    if current_line:
        lines.append(' '.join(current_line))

    return lines

class TextBox:
    def __init__(self, text, location, color, font_name, font_size, font_type='', align='left'):
        """Init the structure

        Args:
            text(str):
            location(tuple(x,y,w,h)):
            color(tuple(r,g,b)):
        """
        self.text = text
        self.location = location
        self.color = color
        self.font_path = FontManager.get_font_path(font_name, font_type)
        self.lines, self.font_size = self.wrap_text_decrease_font(text, location, self.font_path, font_size)
        self.align = align

    @staticmethod
    def wrap_text_decrease_font(text, location, font_path, font_size):
        size_original = font_size
        font = ImageFont.truetype(font_path, font_size)
        wrapped_lines = wrap_text(text, font, location[2])

        # Calculate the total height of the text block
        #line_height = font.getsize("A")[1]  # Height of a single line of text
        ascent, descent = font.getmetrics()
        line_height = ascent + descent
        total_text_height = line_height * len(wrapped_lines)

        # Check if the text height fits within the area height, adjust the font size if needed
        while total_text_height > location[3] and font_size > 5:
            font_size -= 1
            font = ImageFont.truetype(font_path, font_size)
            wrapped_lines = wrap_text(text, font, location[2])
            ascent, descent = font.getmetrics()
            line_height = ascent + descent
            total_text_height = line_height * len(wrapped_lines)

        if size_original == font_size:
            print(f'Font size was not changed')
        else:
            f"Font size was decreased from {size_original} to {font_size}"
        return wrapped_lines, font_size
