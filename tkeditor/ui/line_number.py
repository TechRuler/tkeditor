from tkinter import Canvas, Text
from tkeditor.utils import get_font

class LineNumber(Canvas):
    def __init__(self, master, **kwarg):
        Allowed_keys = Canvas(master).keys()
        super().__init__(master, **{k:v for k, v in kwarg.items() if k in Allowed_keys})
        self.master = master
        self.kwarg = kwarg
        self.text_widget:Text 
        self.fill = kwarg.get('line_number_fg','black')
        self.font = get_font(kwarg.get('font',("TkDefaultFont",9)))
        self.width = kwarg.get('lineboxwidth', 55)
        self.current_line_number = kwarg.get('current_line_number', "steelblue")

        self.char_width = self.font.measure('M')

        self.config(
            highlightthickness=0,
            width=self.width,
            bg=(
                kwarg.get("line_number_bg")
                or kwarg.get("bg")
                or kwarg.get("background")
                or "#ffffff"
            ),
        )

        self.fill = kwarg.get("line_number_fg") if kwarg.get("line_number_fg") else kwarg.get("fg") or kwarg.get("foreground")
    def schedule_redraw(self,event=None):
        self.text_widget.after_idle(self.refresh_lines)
        
    def attach(self, text_widget):
        self.text_widget = text_widget

        
    def refresh_lines(self, event=None):
        self.redraw()

    def redraw(self):
        self.delete('all')
        index = self.text_widget.index("@0,0")
        max_digits = 0
        char_width = self.char_width
        y_to_line = {}  # <-- map y coordinate to the LAST line at that y

        while True:
            dline = self.text_widget.dlineinfo(index)
            if not dline:
                break  # No more visible lines
            
            y = dline[1]
            lineno = index.split('.')[0]
            y_to_line[y] = lineno  # <-- overwrite so last line at y wins
            index = self.text_widget.index(f"{index}+1line")

        for y in sorted(y_to_line):
            lineno = y_to_line[y]
            color: str = self.fill or "#888888"
            if lineno == self.text_widget.index("insert").split('.')[0]:
                color = self.current_line_number or color
            max_digits = max(max_digits, len(lineno))
            x = self.width - len(lineno) * char_width - 5
            self.create_text(x, y, anchor='nw', text=lineno,
                             font=self.font, fill=color,
                             tags=('line_number'))

        # Adjust gutter width if needed
        required_width = max_digits * char_width + 10
        if required_width != self.width:
            self.width = required_width
            self.config(width=self.width)



    def configure(self, **kwarg):
        super().configure(**{k:v for k, v in kwarg.items() if k in Canvas().keys()})
        if "fg" in kwarg:
            self.fill = kwarg.get("fg")
            self.itemconfigure("line_number", fill=kwarg.get("fg"))
        if 'current_line_number' in kwarg:
            self.current_line_number = kwarg.get('current_line_number')
        if 'font' in kwarg:
            self.font = get_font(kwarg.get('font'))
            self.itemconfig("line_number", font=self.font)
        
