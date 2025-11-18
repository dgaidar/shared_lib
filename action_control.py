class ActionControl:
    def __init__(self, master):
        self.master = master
        self.name = None
        self.x = None
        self.y = None
        # Variables to store drag state
        self.drag = {"x": 0, "y": 0}

    def bind(self, event_name, callback, *args, **kwargs):
        supported = ["scroll", "move", "resize"]
        if event_name not in supported:
            raise RuntimeError(f"Unknown event {event_name}. Only {supported} are supported")

        if event_name == "scroll":
            # Bind mouse wheel (Windows / Linux)
            self.master.bind("<MouseWheel>", callback)  # Windows
            self.master.bind("<Button-4>", callback)  # Linux scroll up
            self.master.bind("<Button-5>", callback)  # Linux scroll down
        elif event_name == "move":
            # Bind drag/drop
            self.master.bind("<ButtonPress-1>", callback)
            self.master.bind("<B1-Motion>", args[0])
        elif event_name == "resize":
            # MacOS uses event.delta as well, but with different scaling
            self.master.bind("<Configure>", callback)


class CanvasAction(ActionControl):
    ZOOM_MIN = 0.1
    ZOOM_MAX = 3
    def __init__(self, canvas, move=False, scroll=False, resize=False):
        super().__init__(canvas)
        if move:
            self.bind("move", self.on_press, self.on_drag)
        if scroll:
            self.bind("scroll", self.on_scroll)
        if resize:
            self.bind("resize", self.on_resize)

    def on_press(self, event):
        """Record where the user clicked"""
        self.name = "move"
        self.drag["x"] = event.x
        self.drag["y"] = event.y

    def on_drag(self, event):
        """Compute how far the mouse moved"""
        dx = event.x - self.drag["x"]
        dy = event.y - self.drag["y"]
        self.drag["x"] = event.x
        self.drag["y"] = event.y

        # Move the image
        # TODO:
        #dx, dy = self.restrict_drag(dx, dy)
        canvas = self.master
        for image in canvas.get_images(event):
            self.master.move(image.image_id, dx, dy)

            # Keep the image within bounds
            #self.keep_image_in_bounds()

    def keep_image_in_bounds(self, image):
        """Ensure the image never leaves the visible canvas area."""
        canvas = self.master
        x, y = canvas.coords(image.image_id)
        cw, ch = canvas.winfo_width(), canvas.winfo_height()
        iw, ih = image.display_image.width(), image.display_image.height()

        # Clamp x, y so that at least the canvas area is filled
        if iw > cw:
            x = min(0, max(x, cw - iw))
        else:
            x = (cw - iw) / 2  # center if smaller

        if ih > ch:
            y = min(0, max(y, ch - ih))
        else:
            y = (ch - ih) / 2

        canvas.coords(image.image_id, x, y)

    def on_scroll(self, event):
        """Increase or decrease image size"""
        self.name = "scroll"
        canvas = self.master
        for image in canvas.get_images(event):
            if not image.sample:
                return

            # Determine zoom direction
            if event.num == 5 or event.delta < 0:
                scale = image.sample_scale / 1.1  # zoom out
            elif event.num == 4 or event.delta > 0:
                scale = image.sample_scale * 1.1  # zoom in

            # Clamp scale
            scale = self.apply_limits(scale)

            # Resize and update image
            image.resize(scale)

            # Keep top-left corner fixed
            canvas.config(scrollregion=canvas.bbox("all"))

    # TODO: refactor!
    def apply_limits(self, scale):
        """Check that the current scale is inside min/max borders. If not - fix it"""
        if scale < self.master.ZOOM_MIN:
            return self.master.ZOOM_MIN
        if scale > self.master.ZOOM_MAX:
            return self.master.ZOOM_MAX
        return scale

    def on_resize(self, event):
        """
        Keep image scaled so it's never smaller than the canvas area.
        Triggered on <Configure> (resize) event.
        """
        self.name = "resize"
        for image in self.master.get_images(event):
            if not image.sample:
                # Nothing shown
                return

            # Get new canvas size
            canvas_w = event.width
            canvas_h = event.height

            # Original image size
            orig_w, orig_h = image.sample.size

            # Compute minimum scale so image covers canvas completely
            scale_w = canvas_w / orig_w
            scale_h = canvas_h / orig_h
            new_scale = min(scale_w, scale_h)  # ensures image >= canvas in both directions

            # Update only if scale changed significantly (optional optimization)
            if abs(new_scale - image.sample_scale) < 0.01:
                return

            image.resize(new_scale)

