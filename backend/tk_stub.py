"""Заглушка tkinter для headless-окружения (Docker)."""
import sys
import types


def install() -> None:
    if "tkinter" in sys.modules:
        return

    class _Widget:
        def __init__(self, *args, **kwargs):
            pass

        def pack(self, *args, **kwargs):
            return None

        def grid(self, *args, **kwargs):
            return None

        def bind(self, *args, **kwargs):
            return None

        def config(self, *args, **kwargs):
            return None

        def destroy(self, *args, **kwargs):
            return None

        def insert(self, *args, **kwargs):
            return None

        def get(self, *args, **kwargs):
            return ""

    class _Var:
        def __init__(self, value=""):
            self._value = value

        def get(self):
            return self._value

        def set(self, value):
            self._value = value

    class _Text(_Widget):
        def get(self, *args, **kwargs):
            return ""

    class _Tk(_Widget):
        def title(self, *args, **kwargs):
            return None

        def geometry(self, *args, **kwargs):
            return None

        def minsize(self, *args, **kwargs):
            return None

        def mainloop(self, *args, **kwargs):
            return None

    class _Canvas(_Widget):
        def create_window(self, *args, **kwargs):
            return None

        def configure(self, *args, **kwargs):
            return None

        def yview(self, *args, **kwargs):
            return None

        def xview(self, *args, **kwargs):
            return None

        def bbox(self, *args, **kwargs):
            return (0, 0, 0, 0)

    tk = types.ModuleType("tkinter")
    tk.END = "end"
    tk.W = "w"
    tk.E = "e"
    tk.N = "n"
    tk.S = "s"
    tk.X = "x"
    tk.Y = "y"
    tk.BOTH = "both"
    tk.LEFT = "left"
    tk.RIGHT = "right"
    tk.TOP = "top"
    tk.BOTTOM = "bottom"
    tk.HORIZONTAL = "horizontal"
    tk.VERTICAL = "vertical"
    tk.StringVar = _Var
    tk.IntVar = _Var
    tk.BooleanVar = _Var
    tk.Frame = _Widget
    tk.Label = _Widget
    tk.Entry = _Widget
    tk.Text = _Text
    tk.Button = _Widget
    tk.Canvas = _Canvas
    tk.LabelFrame = _Widget
    tk.Radiobutton = _Widget
    tk.Checkbutton = _Widget
    tk.Tk = _Tk

    filedialog = types.ModuleType("tkinter.filedialog")
    filedialog.askopenfilename = lambda **kwargs: ""

    messagebox = types.ModuleType("tkinter.messagebox")
    messagebox.showwarning = lambda *args, **kwargs: None
    messagebox.showinfo = lambda *args, **kwargs: None

    ttk = types.ModuleType("tkinter.ttk")
    ttk.Combobox = _Widget
    ttk.LabelFrame = _Widget
    ttk.Scrollbar = _Widget

    class _Style:
        def configure(self, *args, **kwargs):
            return None

    ttk.Style = _Style

    sys.modules["tkinter"] = tk
    sys.modules["tkinter.filedialog"] = filedialog
    sys.modules["tkinter.messagebox"] = messagebox
    sys.modules["tkinter.ttk"] = ttk
