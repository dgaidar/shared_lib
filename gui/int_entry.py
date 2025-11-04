import tkinter as tk
from tkinter import ttk


class IntEntry(ttk.Entry):
    """Entry widget that accepts only integers."""

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.var = tk.StringVar()
        self.config(textvariable=self.var)
        self.var.trace_add("write", self._validate)

    def _validate(self, *args):
        val = self.var.get()
        if val in ("", "-"):  # allow temporary input
            return
        if not val.lstrip("-").isdigit():
            # remove invalid characters
            self.var.set(''.join([c for c in val if c.isdigit() or c == '-']))

    def get_int(self):
        """Return current value as int (or None if empty)."""
        val = self.var.get()
        try:
            return int(val)
        except ValueError:
            return None

    def set_int(self, value):
        """Set the entry to a given integer."""
        self.var.set(str(value))
