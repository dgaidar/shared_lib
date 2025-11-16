'''
Display two images and allow merge them
'''
import tkinter as tk
from shared_lib.img_process import resize_and_crop
from shared_lib.gui.widget_preview_file import WidgetPreviewFile
import os
from PIL import Image, ImageTk


class WidgetOverlay(tk.Frame):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bd", 2)
        kwargs.setdefault("relief", "solid")
        super().__init__(parent, **kwargs)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)

        self.overlays = []

        # Mouse drag/scale tracking
        self.drag = {"x": 0, "y": 0}
        self.is_dragging = False

        self.background = WidgetPreviewFile(self, "history/merge_src.json")
        self.background.grid(row=0, rowspan=3, column=0, padx=5, pady=5, sticky="snew")
        self.background.canvas.bind("<MouseWheel>", self.on_scroll)

        self.overlay = WidgetPreviewFile(self, "history/merge_from.json")
        self.overlay.grid(row=0, rowspan=3, column=2, padx=5, pady=5, sticky="snew")

        # Interaction ##########################################################
        btn_add = tk.Button(self, text="<", command=self.add_overlay)
        btn_del = tk.Button(self, text=">", command=self.remove_overlay)
        btn_add.grid(row=1, column=1, padx=5, pady=5, sticky="swe")
        btn_del.grid(row=2, column=1, padx=5, pady=5, sticky="swe")

    # === Add overlay image ===
    def add_overlay(self):
    #def draw_img2_on_img1(self):
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
            anchor="center"
        )
        img2.canvas.itemconfig(img2.image_id, image=img2.display_image)

        # Bring img2 above img1
        img2.canvas.tag_raise(img2.image_id, img1.image_id)

    def remove_overlay(self):
        if self.overlay.canvas.image.image_id:
            self.background.canvas.delete(self.overlay.canvas.image.image_id)
            self.overlay.canvas.image.image_id = None
            self.overlay_tk = None
            self.overlay_scale = 1.0

        # === Drag behavior ===

    def start_drag(self, event):
        if not self.overlay.canvas.image.image_id:
            return
        self.is_dragging = True
        self.drag["x"] = event.x
        self.drag["y"] = event.y

    def on_drag(self, event):
        if not self.is_dragging or not self.overlay.canvas.image.image_id:
            return

        dx = event.x - self.drag["x"]
        dy = event.y - self.drag["y"]
        self.drag["x"], self.drag["y"] = event.x, event.y
        self.background.canvas.move(self.overlay.canvas.image.image_id, dx, dy)

        # === Scroll scaling ===

    def on_scroll(self, event):
        img_background = self.background.canvas.image
        if not img_background.image_id:
            return

        # Determine scroll direction
        if event.num == 5 or event.delta < 0:
            scale_factor = 0.9
        else:
            scale_factor = 1.1

        for img in self.overlays:
            x, y = self.background.canvas.coords(img.image_id)
            w = img.display_image.width()
            h = img.display_image.height()

            if (event.x, event.y) in img:
                scale = img.sample_scale * scale_factor
                img.resize(scale)
                return
        for img in self.overlays:
            img.resize(img.sample_scale * scale_factor)
        img_background.resize(img_background.sample_scale * scale_factor)


    @staticmethod
    def check_folder(path):
        if not path:
            raise RuntimeError("Path not provided")
        if not os.path.exists(path):
            raise RuntimeError(F"Path '{path}' doesn't exist")
        if not os.path.isdir(path):
            raise RuntimeError(F"Path '{path}' not a folder")

    def run(self):
        new_size = self.settings.get_size()
        src = self.panel_src_file.var_path.get()
        dst = self.panel_dst_folder.var_path.get()
        self.check_folder(dst)
        for fname in os.listdir(src):
            fpath = os.path.join(src, fname)
            if fpath in self.background.canvas.path2image:
                img = self.background.canvas.path2image[fpath]
                resized = resize_and_crop(img, new_size)
                resized.save(os.path.join(dst, fname))


