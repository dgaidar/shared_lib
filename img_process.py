import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from .textbox import wrap_text
'''im_pil = Image.fromarray(img)

# For reversing the operation:
im_np = np.asarray(im_pil)'''

"""
def blur_rectangle(img, rect_coords, output_path='output_image.jpg', blur_strength=(15, 15), std_dev=0):
    # Ensure the kernel size is odd and positive
    blur_strength = (blur_strength[0] | 1, blur_strength[1] | 1)  # Making sure both dimensions are odd numbers

    # Load the image using OpenCV
    img_cv = np.asarray(img)

    if img_cv is None:
        raise RuntimeError(f"Error: Unable to convert image from PIL to OpenCV format")

    # Extract rectangle coordinates
    #x, y, w, h = rect_coords.get(units='pixel', height=img_cv.shape[0], width=img_cv.shape[1])
    x, y, w, h = rect_coords

    # Get the region of the image to be blurred (ROI)
    roi = img_cv[y:y + h, x:x + w]

    # Apply a Gaussian blur on the region of interest (ROI)
    roi_blurred = cv2.GaussianBlur(roi, blur_strength, std_dev)  # Standard deviation set to 0 lets OpenCV compute it

    # Replace the original region with the blurred one
    img_cv[y:y + h, x:x + w] = roi_blurred

    # Save the result image using OpenCV
    cv2.imwrite(output_path, img_cv)
    #print(f"Image saved as {output_path}")


def blur_rectangle2(image_path, rect_coords, output_path='output_image.jpg', blur_strength=(15, 15), std_dev=0):
    # Ensure the kernel size is odd and positive
    blur_strength = (blur_strength[0] | 1, blur_strength[1] | 1)  # Making sure both dimensions are odd numbers

    # Load the image using OpenCV
    img_cv = cv2.imread(image_path)

    if img_cv is None:
        print(f"Error: Unable to load image from {image_path}")
        return

    # Extract rectangle coordinates
    #x, y, w, h = rect_coords.get(units='pixel', height=img_cv.shape[0], width=img_cv.shape[1])
    x, y, w, h = rect_coords

    # Get the region of the image to be blurred (ROI)
    roi = img_cv[y:y + h, x:x + w]

    # Apply a Gaussian blur on the region of interest (ROI)
    roi_blurred = cv2.GaussianBlur(roi, blur_strength, std_dev)  # Standard deviation set to 0 lets OpenCV compute it

    # Replace the original region with the blurred one
    img_cv[y:y + h, x:x + w] = roi_blurred

    # Save the result image using OpenCV
    cv2.imwrite(output_path, img_cv)
    #print(f"Image saved as {output_path}")
"""


import fitz  # PyMuPDF
from pathlib import Path


def pdf_to_png(input_pdf, output_folder, zoom_x=2.0, zoom_y=2.0):
    """
    Converts each page of a PDF to a high-quality PNG image.

    Parameters:
    - input_pdf: str, the path to the input PDF file.
    - output_folder: str, the folder where the PNG images will be saved.
    - zoom_x: float, horizontal zoom factor (default 2.0 for high quality).
    - zoom_y: float, vertical zoom factor (default 2.0 for high quality).
    """

    # Open the PDF
    doc = fitz.open(input_pdf)

    for page_num in range(len(doc)):
        # Load each page
        page = doc.load_page(page_num)

        # Set zoom matrix for high resolution (default is 2x)
        matrix = fitz.Matrix(zoom_x, zoom_y)

        # Render the page to a pixmap (image)
        pix = page.get_pixmap(matrix=matrix)

        # Define the output PNG image path
        output_path = f"{output_folder}/page_{page_num + 1}.png"

        # Save the image as PNG
        pix.save(output_path)

        print(f"Page {page_num + 1} saved as {output_path}")

    # Close the PDF document
    doc.close()


def add_mirror_frame(img, percent):
    frame_size = int(min(img.width, img.height) * percent / 100)
    new_image = Image.new('RGB', (img.width + 2 * frame_size, img.height + 2 * frame_size), (255, 255, 255))
    new_image.paste(img, (frame_size, frame_size))

    flipped = img.transpose(Image.FLIP_TOP_BOTTOM)
    new_image.paste(flipped, (frame_size, img.height + frame_size))
    new_image.paste(flipped, (frame_size, frame_size - img.height))

    flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
    new_image.paste(flipped, (frame_size - img.width, frame_size))
    new_image.paste(flipped, (frame_size + img.width, frame_size))

    flipped = flipped.transpose(Image.FLIP_TOP_BOTTOM)
    new_image.paste(flipped, (frame_size - img.width, frame_size - img.height))
    new_image.paste(flipped, (frame_size + img.width, frame_size + img.height))
    new_image.paste(flipped, (frame_size - img.width, frame_size + img.height))
    new_image.paste(flipped, (frame_size + img.width, frame_size - img.height))

    return new_image


def INT_ROUND_UP(num):
    res = int(num) + int(num - int(num) > 0)
    return res


def stratch_left(img, percent, step):
    delta_single = int(img.width * step / 100)
    steps = INT_ROUND_UP(percent / step)
    delta_whole = delta_single * steps
    new_image = Image.new('RGB', (img.width + delta_whole, img.height), (255, 255, 255))
    new_image.paste(img, (delta_whole, 0))

    part = img.crop((0, 0, delta_single, img.height))
    flipped = part.transpose(Image.FLIP_LEFT_RIGHT)
    for i in range(steps):
        added = flipped if (i % 2 == 0) else part
        new_image.paste(added, (delta_whole - (i + 1) * delta_single, 0))
    return new_image


def stratch_right(img, percent, step):
    delta_single = int(img.width * step / 100)
    steps = INT_ROUND_UP(percent / step)
    delta_whole = delta_single * steps
    new_image = Image.new('RGB', (img.width + delta_whole, img.height), (255, 255, 255))
    new_image.paste(img, (0, 0))

    part = img.crop((img.width - delta_single, 0, img.width, img.height))
    flipped = part.transpose(Image.FLIP_LEFT_RIGHT)
    for i in range(steps):
        added = flipped if (i % 2 == 0) else part
        new_image.paste(added, (img.width + i * delta_single, 0))
    return new_image


def add_frame(input_pdf, output_pdf, ratio=10):
    # Open the input PDF
    input_doc = fitz.open(input_pdf)

    # Create a new output PDF
    output_doc = fitz.open()

    for page_num in range(len(input_doc)):
        # Load the original page
        original_page = input_doc.load_page(page_num)

        # Get the dimensions of the original page
        page_width = original_page.rect.width
        page_height = original_page.rect.height

        # Create a new page in the output PDF with double the width to hold both the original and mirrored content
        delta_width = int(page_width * (ratio / 100))
        delta_height = int(page_height * (ratio / 100))
        new_height = page_height + 2 * delta_height
        new_width = page_width + 2 * delta_width
        new_page = output_doc.new_page(width=new_width, height=new_height)

        # Render the original page as a pixmap (image)
        original_pix = original_page.get_pixmap()

        # Insert the original image on the middle of the new page
        new_page.insert_image(fitz.Rect(delta_width,
                                        delta_height,
                                        page_width + delta_width,
                                        page_height + delta_height), pixmap=original_pix)
        #new_page.insert_image(fitz.Rect(delta_width - page_width, delta_height, page_width, page_height), pixmap=original_pix)

        # Create a transformation matrix for horizontal mirroring
        # (-1, 1) scaling flips horizontally
        flip_h = fitz.Matrix(-1, 1)
        flip_v = fitz.Matrix(1, -1)
        flip_hv = fitz.Matrix(-1, -1)

        # Apply the transformation to the mirrored pixmap and adjust its position
        mirrored_h = original_page.get_pixmap(matrix=flip_h)
        mirrored_v = original_page.get_pixmap(matrix=flip_v)
        mirrored_hv = original_page.get_pixmap(matrix=flip_hv)

        # Insert the mirrored image on the right side of the new page
        # Offset it by page_width to the right
        # L/U/R/B
        new_page.insert_image(fitz.Rect(delta_width - page_width,
                                        delta_height,
                                        delta_width,
                                        delta_height + page_height), pixmap=mirrored_h)
        new_page.insert_image(fitz.Rect(delta_width,
                                        delta_height - page_height,
                                        delta_width + page_width,
                                        delta_height), pixmap=mirrored_v)
        new_page.insert_image(fitz.Rect(delta_width + page_width,
                                        delta_height,
                                        delta_width + 2 * page_width,
                                        delta_height + page_height), pixmap=mirrored_h)
        new_page.insert_image(fitz.Rect(delta_width,
                                        delta_height + page_height,
                                        delta_width + page_width,
                                        delta_height + 2 * page_height), pixmap=mirrored_v)

        #
        new_page.insert_image(fitz.Rect(delta_width - page_width,
                                        delta_height - page_height,
                                        delta_width,
                                        delta_height), pixmap=mirrored_hv)
        new_page.insert_image(fitz.Rect(delta_width - page_width,
                                        delta_height + page_height,
                                        delta_width,
                                        delta_height + 2 * page_height), pixmap=mirrored_hv)
        new_page.insert_image(fitz.Rect(page_width + delta_width,
                                        delta_height - page_height,
                                        2 * page_width + delta_width,
                                        delta_height), pixmap=mirrored_hv)
        new_page.insert_image(fitz.Rect(page_width + delta_width,
                                        page_height + delta_height,
                                        2 * page_width + delta_width,
                                        2 * page_height + delta_height), pixmap=mirrored_hv)

    # Save the output PDF
    output_doc.save(output_pdf)
    output_doc.close()
    input_doc.close()


def merge(card, back):
    """Combine a card image with its back image"""
    size = (back.size[0] * 2, back.size[1])
    delta = int((size[1] - card.size[1]) / 2)
    new_image = Image.new('RGB', size, (255, 255, 255))
    new_image.paste(back, (0, 0))
    new_image.paste(card, (back.size[0], delta))
    return new_image


def remove_color_and_replace_with_background(img, color_to_remove, area_coords, threshold=120):
    """
    Removes a specified color from a defined area in the image and replaces it with surrounding background.

    Parameters:
        image_path (str): Path to the input image.
        color_to_remove (tuple): The BGR color to remove (e.g., (255, 0, 0) for blue).
        area_coords (tuple): Coordinates of the rectangular area to process (x, y, width, height).
        threshold (int): Tolerance range for color matching.

    Returns:
        result (ndarray): The processed image.
    """
    # Load the image
    img = np.asarray(img).copy()
    #img.setflags(write=1)
    if img is None:
        raise ValueError("Cannot convert from PIL to OpenCV format")

    # Get image dimensions
    img_height, img_width = img.shape[:2]

    # Extract area coordinates and ensure they're within bounds
    x, y, w, h = area_coords
    x = max(0, min(x, img_width))
    y = max(0, min(y, img_height))
    w = min(w, img_width - x)
    h = min(h, img_height - y)

    # Ensure the area is not empty
    if w == 0 or h == 0:
        raise ValueError("The selected area is out of bounds or has zero width/height.")

    area = img[y:y + h, x:x + w]

    # Convert the image to the Lab color space for better color distance measurement
    lab = cv2.cvtColor(area, cv2.COLOR_BGR2Lab)

    # Convert the target color to Lab space
    color_lab = np.uint8([[list(color_to_remove)]])
    color_lab = cv2.cvtColor(color_lab, cv2.COLOR_BGR2Lab)[0][0]

    # Convert to integers to avoid overflow
    color_lab = color_lab.astype(int)

    # Compute a mask where the target color is detected within a threshold
    lower_bound = np.array(
        [max(0, color_lab[0] - threshold), max(0, color_lab[1] - threshold), max(0, color_lab[2] - threshold)])
    upper_bound = np.array(
        [min(255, color_lab[0] + threshold), min(255, color_lab[1] + threshold), min(255, color_lab[2] + threshold)])

    mask = cv2.inRange(lab, lower_bound, upper_bound)

    # Inpaint (replace the detected color with background using surrounding pixels)
    inpainted_area = cv2.inpaint(area, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

    # Replace the original area with the inpainted one
    img[y:y + h, x:x + w] = inpainted_area

    return Image.fromarray(img)


def write_text_on_image(image, text, text_color, area, font_path, font_size,
                        align='left', rectangle=False):
    """
    Writes text on an image.

    Args:
    - source_image_path: str, path to the source image.
    - text: str, the text to write on the image.
    - text_color: tuple, color of the text (R, G, B).
    - area: tuple, (x, y, width, height) where the text should be placed.
    - font_size: int, size of the text font.
    - font_path: str, optional path to a custom font file (e.g., .ttf). If None, a default font will be used.
    - output_file_name: str, name of the output image file.

    Returns:
    - None
    """

    # Open the source image
    draw = ImageDraw.Draw(image)

    # Define the position and area where the text will be placed
    x, y, width, height = area

    font = ImageFont.truetype(font_path, font_size)
    wrapped_lines = wrap_text(text, font, width)

    # Calculate the total height of the text block
    ascent, descent = font.getmetrics()
    line_height = ascent + descent
    #line_height = font.getsize("A")[1]  # Height of a single line of text
    total_text_height = line_height * len(wrapped_lines)

    # Check if the text height fits within the area height, adjust the font size if needed
    while total_text_height > height:
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)
        wrapped_lines = wrap_text(text, font, width)
        ascent, descent = font.getmetrics()
        line_height = ascent + descent
        total_text_height = line_height * len(wrapped_lines)

    # Write each line of text on the image
    for i, line in enumerate(wrapped_lines):
        line_y = y + i * line_height
        if align == 'left':
            offset = 0
        elif align == 'center':
            offset = int((width - font.getbbox(line)[2]) / 2)
        else:
            offset = int(width - font.getbbox(line)[2])
        draw.text((offset + x, line_y), line, font=font, fill=text_color, align=align)

    if rectangle:
        draw.rectangle([(x, y), (x + width, y + height)], fill=None, outline=None, width=1)

    # Write the text on the image
    #draw.text((x, y), text, font=font, fill=text_color)

    # Save the modified image
    #image.save(output_file_name)
    #print(f"Text written to {output_file_name} successfully.")
    return image


def resize_and_crop(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    """
    Resize the given PIL Image 'img' to fit 'size' exactly,
    preserving aspect ratio by cropping equally from sides or top/bottom.

    Args:
        img: PIL.Image object
        size: (width, height) target size in pixels

    Returns:
        New PIL.Image object resized and cropped to the desired size.
    """
    target_w, target_h = size
    src_w, src_h = img.size

    # Compute aspect ratios
    src_ratio = src_w / src_h
    target_ratio = target_w / target_h

    # Decide whether to crop width or height
    if src_ratio > target_ratio:
        # Source is wider than target → crop left/right
        new_width = int(src_h * target_ratio)
        left = (src_w - new_width) // 2
        right = left + new_width
        top, bottom = 0, src_h
    else:
        # Source is taller than target → crop top/bottom
        new_height = int(src_w / target_ratio)
        top = (src_h - new_height) // 2
        bottom = top + new_height
        left, right = 0, src_w

    # Crop the image
    img_cropped = img.crop((left, top, right, bottom))

    # Resize to target size
    img_resized = img_cropped.resize((target_w, target_h), Image.LANCZOS)
    return img_resized