'''
tk.Frame with file preview controls

Contains:
    WidgetSelectFile
    ZoomableCanvas
    Zoom Control widgets
'''
import tkinter as tk
from shared_lib.icon_mng import IconMng
from shared_lib.gui.zoomable_canvas import ZoomableCanvas
from shared_lib.history import History
from shared_lib.gui.widget_select_file import WidgetSelectFile


class WidgetPreviewFile(tk.Frame):
    ZOOM_MIN = 0.1
    ZOOM_MAX = 3

    def __init__(self, parent, path_history, zoom_min=None, zoom_max=None, **kwargs):
        """Panel with preview widgets"""
        if zoom_max:
            self.zoom_max = zoom_max
        if zoom_min:
            self.zoom_min = zoom_min
        kwargs.setdefault("bd", 2)
        kwargs.setdefault("relief", "solid")
        super().__init__(parent, **kwargs)

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)
        self.columnconfigure(0, weight=1)

        # Source file panel ####################################################
        self.file_select = WidgetSelectFile(self, False,
                                         History(path_history, 20),
                                         init_from_history=False)
        self.file_select.grid(row=0, column=0, padx=5, pady=5, sticky="new")

        # File preview scrollable panel
        self.canvas = ZoomableCanvas(self)
        self.canvas.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.make_zoom_control()
        self.zoom_control.grid(row=2, column=0, padx=5, pady=5, sticky="s")

        # Canvas: Mouse wheel movement (zoom in/out)
        self.canvas.bind("<MouseWheel>", self.on_zoom)  # Windows
        self.canvas.bind("<Button-4>", self.on_zoom)  # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_zoom)  # Linux scroll down

        # File select: src file is choosen
        self.file_select.var_path.trace_add("write", self.load)  # fires on .set() or user change

    def make_zoom_control(self):
        self.zoom_control = tk.Frame(self, bd=2, relief="solid")
        self.icon = IconMng.get_img("ZoomDisplayWhole")
        self.zoom_control.btn_full = tk.Button(self.zoom_control,
                                               image=self.icon, command=self.zoom_full)

        self.zoom_control.columnconfigure(0, weight=0)
        self.zoom_control.rowconfigure(0, weight=1)
        self.zoom_control.btn_full.grid(row=0, column=0, padx=5, pady=5, sticky="nsw")

        # Slider: horizontal zoom
        self.zoom_control.slider = tk.Scale(
            self.zoom_control, from_=self.zoom_min, to=self.zoom_max, resolution=0.01,
            orient="horizontal", length=200,
            showvalue=True,
            command=self.slider_changed
        )
        self.zoom_control.slider.grid(row=0, column=1, padx=5, pady=5, sticky="nse")

    def apply_limits(self, scale):
        """Check that the current scale is inside min/max borders. If not - fix it"""
        if scale < self.ZOOM_MIN:
            return self.ZOOM_MIN
        if scale > self.ZOOM_MAX:
            return self.ZOOM_MAX
        return scale

    def on_zoom(self, event):
        """Increase or decrease image size"""
        if not self.canvas.image.img_original:
            return

        # Determine zoom direction
        if event.num == 5 or event.delta < 0:
            self.canvas.image.sample_scale /= 1.1  # zoom out
        elif event.num == 4 or event.delta > 0:
            self.canvas.image.sample_scale *= 1.1  # zoom in

        # Clamp scale
        scale = self.apply_limits(self.canvas.image.sample_scale)
        self.canvas.image.sample_scale = scale
        self.zoom_control.slider.set(scale)

        # Resize and update image
        self.canvas.image.resize(scale)

        # Keep top-left corner fixed
        self.canvas.config(scrollregion=self.bbox("all"))

    def zoom_full(self):
        """Draw the image on canvas (max size, the whole image is visible)"""
        if self.canvas.image is None or self.canvas.image.sample is None:
            return
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image_width = self.canvas.image.sample.width
        image_height = self.canvas.image.sample.height
        if image_width == 0 or image_height == 0:
            return 1.0  # Avoid division by zero
        if canvas_width == 1:
            canvas_width = self.zoom_control.winfo_width()
            canvas_height = self.zoom_control.winfo_height()
        scale_w = canvas_width / image_width
        scale_h = canvas_height / image_height

        all_visible = False
        if all_visible:
            scale = max(scale_w, scale_h)
        else:
            scale = min(scale_w, scale_h)

        self.canvas.image.resize(scale)
        self.zoom_control.slider.set(scale)


    def slider_changed(self, *args):
        """Indicates that slider was moved"""
        scale = self.zoom_control.slider.get()
        self.canvas.image.resize(scale)


    def load(self, *args):
        """Load image"""
        path = self.file_select.var_path.get()
        self.canvas.load(path)
        self.zoom_control.slider.set(self.canvas.image.sample_scale)

