from PIL import Image
from shared_lib.image_info import ImageInfo
from typing import List


class CanvasDump:
    def __init__(self, canvas):
        self.canvas = canvas

    def dump(self, path, format="PNG"):
        # Detect Canvas and Images
        canvas = self.canvas
        images: List[ImageInfo] = canvas.get_images()

        background = images[0]
        w = background.img_original.width
        h = background.img_original.height

        # Create blank result image
        result = Image.new("RGBA", (w, h), (255, 255, 255, 0))

        # Calculate new sizes for images to paste
        scale_bg = background.img_scale * background.sample_scale

        for img in images:
            # Resize if needed
            img_scale = scale_bg / (img.img_scale * img.sample_scale)
            resized = img.img_original.resize(
                (int(img.img_original.width * img_scale),
                 int(img.img_original.height * img_scale)),
                resample=Image.LANCZOS,
            )

            # Offset
            x, y = canvas.coords(img.image_id)
            x, y = int(x * img_scale), int(y * img_scale)

            # Paste
            result.paste(resized, box=(x, y), mask=resized.convert("RGBA"))

        # Save file
        if not str(path).endswith(f".{format}"):
            path = str(path) + "." + format
        result.save(path, format=format)
