'''
Display two images and allow merge them
'''
import tkinter as tk
from shared_lib.img_process import resize_and_crop
from shared_lib.gui.widget_preview_file import WidgetPreviewFile
import os
from PIL import Image, ImageTk
from shared_lib.gui.error import Error


class WidgetOverlay(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)

        self.overlays = []  # List[ImageInfo]

        self.background = WidgetPreviewFile(self, "history/merge_src.json")
        self.background.grid(row=0, rowspan=3, column=0, padx=5, pady=5, sticky="snew")
        def get_images(event=None):
            if not event:
                images = [self.background.canvas.image] + self.overlays
                return images
            (x, y) = (event.x, event.y)
            images = []
            for img in self.overlays:
                if (x, y) in img:
                    images.append(img)

            # We move/scale either a single image or all images
            if len(images) == 0 or len(images) > 1:
                images = [img for img in self.overlays]
                images.append(self.background.canvas.image)
            return images
        self.background.canvas.get_images = get_images


        self.overlay = WidgetPreviewFile(self, "history/merge_from.json")
        self.overlay.grid(row=0, rowspan=3, column=2, padx=5, pady=5, sticky="snew")

        # Interaction ##########################################################
        btn_add = tk.Button(self, text="<", command=self.add_overlay)
        btn_del = tk.Button(self, text=">", command=self.remove_overlay)
        btn_add.grid(row=1, column=1, padx=5, pady=5, sticky="swe")
        btn_del.grid(row=2, column=1, padx=5, pady=5, sticky="swe")

    # === Add overlay image ===
    def add_overlay(self):
        img1 = self.background.canvas.image
        img2 = self.overlay.canvas.image.copy()

        # Convert img2 PIL to PhotoImage for img1.canvas
        img2.canvas = img1.canvas
        self.overlays.append(img2)

        w, h = img2.sample.width, img2.sample.height
        resized = img2.sample.resize((int(w*img2.sample_scale), int(h*img2.sample_scale)), Image.LANCZOS)
        img2.display_image = ImageTk.PhotoImage(resized)
        img2.image_id = img2.canvas.create_image(
            img2.display_image.width() // 2,
            img2.display_image.height() // 2,
            image=img2.display_image,
            anchor="nw"
        )
        img2.canvas.itemconfig(img2.image_id, image=img2.display_image)

        # Bring img2 above img1
        img2.canvas.tag_raise(img2.image_id, img1.image_id)

    def remove_overlay(self):
        if len(self.overlays) == 1:
            self.background.canvas.delete(self.overlays[0].image_id)
            self.overlays.pop()
        else:
            # What image should we remove?
            path = self.overlay.file_select.get_path()
            for i, img in enumerate(self.overlays):
                if img.path == path:
                    self.background.canvas.delete(img.image_id)
                    self.overlays.pop(i)
                    return

            Error.show(f"Don't know what image you want to delete."
                       f"\nPlease set it on the right panel")

    @staticmethod
    def check_folder(path):
        if not path:
            raise RuntimeError("Path not provided")
        if not os.path.exists(path):
            raise RuntimeError(F"Path '{path}' doesn't exist")
        if not os.path.isdir(path):
            raise RuntimeError(F"Path '{path}' not a folder")
