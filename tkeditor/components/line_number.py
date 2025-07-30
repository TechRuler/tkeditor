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
        index = self.text_widget.index("@0,0")
        max_digits = 0
        char_width = self.char_width
        seen_y = set()

        while True:
            dline = self.text_widget.dlineinfo(index)
            if not dline:
                break  # No more visible lines

            y = dline[1]
            if y in seen_y:
                # Prevent multiple line numbers at same y-coordinate
                index = self.text_widget.index(f"{index}+1line")
                continue
            seen_y.add(y)

            lineno = index.split('.')[0]
            max_digits = max(max_digits, len(lineno))
            x = self.width - len(lineno) * char_width - 5

            self.create_text(x, y, anchor='nw', text=lineno,
                            font=self.font, fill=self.fill,
                            tags=('line_number'))

            index = self.text_widget.index(f"{index}+1line")

        # Adjust gutter width if needed
        required_width = max_digits * char_width + 10
        if required_width != self.width:
            self.width = required_width
            self.config(width=self.width)


    def configure(self, **kwarg):
        super().configure(**kwarg)
        if "line_number_fg" in kwarg:
            self.itemconfigure("line_number", fill=self.kwarg.get("line_number_fg"))
