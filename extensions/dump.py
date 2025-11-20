from PIL import Image
from shared_lib.image_info import ImageInfo
from typing import List
from shared_lib.logger import get_file_logger
from shared_lib.img_process import img_paste


logger = get_file_logger()


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
        logger.debug(f"Background original: {w}x{h}")
        logger.debug(f"Background scaled: {background.sample.width}x{background.sample.height}")

        # Create blank result image
        result = Image.new("RGBA", (w, h), (255, 255, 255, 0))

        # Calculate new sizes for images to paste
        scale_bg = background.img_scale * background.sample_scale
        logger.debug(f"Background scale = {background.img_scale} * {background.sample_scale} = {scale_bg}")

        for img in images:
            img_scale = img.img_scale * img.sample_scale / scale_bg
            x, y = canvas.coords(img.image_id)
            x, y = int(x / scale_bg), int(y / scale_bg)
            w = int(img.img_original.width * img_scale)
            h = int(img.img_original.height * img_scale)
            img_paste(result, img.img_original, x, y, w, h)

        # Save file
        if not str(path).endswith(f".{format}"):
            path = str(path) + "." + format
        result.save(path, format=format)
