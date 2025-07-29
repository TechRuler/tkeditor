from tkinter import Canvas

class FoldingCode(Canvas):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **{k: v for k, v in kwargs.items() if k in Canvas(master).keys()})
        self.font = kwargs.get('font', ('Consolas', 10))
        self.configure(
            width=kwargs.get('folding_width', 20),
            bg=kwargs.get('bg', '#2b2b2b'),
            highlightthickness=0
        )
        self.text_widget = None

    def attach(self, text_widget):
        self.text_widget = text_widget
        for event in ("<Configure>", "<KeyRelease>", "<MouseWheel>", "<ButtonRelease-1>"):
            self.text_widget.bind(event, self._schedule_draw, add="+")
        self._schedule_draw()

    def _schedule_draw(self, event=None):
        if not hasattr(self, "_draw_scheduled") or not self._draw_scheduled:
            self._draw_scheduled = True
            self.after_idle(self._draw_folding_lines)

    def _draw_folding_lines(self):
        self._draw_scheduled = False
        self.delete("folding_line")
        if not self.text_widget:
            return

        index = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(index)
            if dline is None:
                break

            y = dline[1]
            lineno = index.split(".")[0]
            line_text = self.text_widget.get(f"{lineno}.0", f"{lineno}.end").strip()

            x = 10  # center gutter

            if line_text.startswith("class") or line_text.startswith("def"):
                # Draw + button and |- branch
                self.create_text(x, y, text="+", anchor="center", font=self.font, fill="#aaa", tags="folding_line")
                self.create_line(x, y + 12, x, y + 20, fill="#888", tags="folding_line")  # |- vertical stem
                self.create_line(x, y + 20, x + 5, y + 20, fill="#888", tags="folding_line")  # horizontal branch
            elif line_text:
                # Draw vertical continuation line |
                self.create_line(x, y, x, y + 16, fill="#555", tags="folding_line")

            index = self.text_widget.index(f"{index}+1line")
