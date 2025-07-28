from tkinter import Canvas
from tkinter.font import Font
from tkeditor.utils import get_font

class LineNumber(Canvas):
    def __init__(self, master, **kwarg):
        super().__init__(master, **{k:v for k, v in kwarg.items() if k in Canvas(master).keys()})
        self.master = master
        self.kwarg = kwarg
        self.text_widget = None
        self.fill = kwarg.get('line_number_fg','black')
        self.font = get_font(kwarg.get('font',("TkDefaultFont",9)))
        self.width = kwarg.get('width', 55)

        self.char_width = self.font.measure('M')

        self.config(width=self.width, 
                    bg=kwarg.get("line_number_bg") if kwarg.get("line_number_bg") else kwarg.get('bg') or kwarg.get("background")
                    )
        self.fill = kwarg.get("line_number_fg") if kwarg.get("line_number_fg") else kwarg.get("fg") or kwarg.get("foreground")
    def attach(self, text_widget):
        self.text_widget = text_widget

        def schedule_redraw(event=None):
            self.text_widget.after_idle(self.refresh_lines)

        self.text_widget.bind("<KeyRelease>", schedule_redraw, add="+")
        self.text_widget.bind("<MouseWheel>", schedule_redraw, add="+")
        self.text_widget.bind("<Button-1>", schedule_redraw, add="+")
        self.text_widget.bind("<Configure>", schedule_redraw, add="+")
        self.text_widget.bind("<<Redraw>>", schedule_redraw)

    def refresh_lines(self, event=None):
        self.redraw()

    def redraw(self):
        self.delete('all')
        a = self.text_widget.index("@0,0")

        while True:
            dline = self.text_widget.dlineinfo(a)
            if not dline:
                break
            y = dline[1]
            line_number = str(a).split('.')[0]
            x = self.width - len(line_number)*self.char_width - 5
            if len(line_number)*self.char_width > self.width - 5:
                self.width = len(line_number)*self.char_width
                self.config(width=self.width)
            self.create_text(x, y, anchor='nw', text=line_number, 
                             font=self.font, 
                             fill=self.fill,
                             tags=('line_number')
                             )
            a = self.text_widget.index(f"{a}+1line")
    def configure(self, **kwarg):
        super().configure(**kwarg)
        if "line_number_fg" in kwarg:
            self.itemconfigure("line_number", fill=self.kwarg.get("line_number_fg"))
