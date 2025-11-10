import tkinter as tk
from tkinter import Image
from PIL import Image, ImageTk, ImageDraw, ImageFont
from .font import FontManager


def text_to_img(text, width, height, font_name="times new roman",
                font_type="",
                font_size=14,
                offset=5,
                text_color="black",
                bg_color="white"):
    # Load font
    font_path = FontManager.get_font_path(font_name, font_type)
    font = ImageFont.truetype(font_path or "arial.ttf", font_size)

    # Create a temporary image to measure text
    temp_img = Image.new("RGB", (width-2*offset, height), bg_color)
    draw = ImageDraw.Draw(temp_img)

    # Manual word wrapping
    lines = []
    lines_original = text.split('\n')
    current_line = ""
    for line in lines_original:
        for word in line.split():
            test_line = f"{current_line} {word}".strip()
            w = draw.textlength(test_line, font=font)
            if w <= width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        current_line = ""

    # Calculate image height
    line_height = font.getbbox("A")[3] - font.getbbox("A")[1]
    img_height = line_height * len(lines) + offset * (len(lines) - 1) + 20

    # Create final image
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Draw text line by line
    y = offset
    for line in lines:
        draw.text((offset, y), line, font=font, fill=text_color)
        y += line_height + offset
        if y + line_height > height:
            break

    # Convert to Tkinter PhotoImage
    #return ImageTk.PhotoImage(img)
    return img