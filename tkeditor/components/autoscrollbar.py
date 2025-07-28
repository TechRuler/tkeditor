from tkinter import ttk, TclError
class AutoScrollbar(ttk.Scrollbar):
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
        ttk.Scrollbar.set(self, lo, hi)
    def pack(self):
        return TclError('Cannot use pack with this widget')
    def place(self):
        return TclError('Cannot use place with this widget')
    