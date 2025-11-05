from tkinter import messagebox


class Error:
    """Provides Error MessageBox"""
    @classmethod
    def show(cls, msg):
        """Provides Error MessageBox"""
        messagebox.showerror("Error", msg)

    @classmethod
    def fatal(cls, msg):
        """Print error and crash"""
        cls.show(msg)
        exit(1)

