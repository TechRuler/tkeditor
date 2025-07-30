import tkinter as tk
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
        self.folded_blocks = {}  # key: start line, value: end line
        self.tag_prefix = "folded_"

    def attach(self, text_widget):
        self.text_widget = text_widget
        for event in ("<Configure>", "<KeyRelease>", "<MouseWheel>", "<ButtonRelease-1>"):
            self.text_widget.bind(event, self._schedule_draw, add="+")
        self.bind("<Button-1>", self._on_click)
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
            line_text = self.text_widget.get(f"{lineno}.0", f"{lineno}.end")

            x = 5  # Gutter margin

            # Detect foldable lines (you can expand this)
            if line_text.strip().startswith(("class ", "def ", "if ", "for ", "while ")):
                folded = lineno in self.folded_blocks
                symbol = "+" if folded else "-"
                self.create_text(x, y, text=symbol, anchor="nw", font=self.font, fill="#aaa", tags=("folding_line", f"line_{lineno}"))

            index = self.text_widget.index(f"{index}+1line")

    def _on_click(self, event):
        clicked = self.find_withtag("current")
        if not clicked:
            return
        tags = self.gettags(clicked[0])
        line_tag = next((tag for tag in tags if tag.startswith("line_")), None)
        if not line_tag:
            return
        lineno = line_tag.replace("line_", "")
        if lineno in self.folded_blocks:
            self._unfold_block(lineno)
        else:
            self._fold_block(lineno)

    def _fold_block(self, start_line):
        start_index = f"{start_line}.0"
        end_index = self._find_block_end(start_index)
        if not end_index:
            return

        tag = self.tag_prefix + start_line
        self.text_widget.tag_add(tag, f"{start_index}+1line", end_index)
        self.text_widget.tag_configure(tag, elide=True)
        self.folded_blocks[start_line] = end_index.split(".")[0]
        self.text_widget.event_generate("<<Redraw>>")  # ✅ Trigger line number redraw
        self._schedule_draw()

    def _unfold_block(self, start_line):
        tag = self.tag_prefix + start_line
        self.text_widget.tag_remove(tag, f"{start_line}.0", f"{self.folded_blocks[start_line]}.end")
        self.folded_blocks.pop(start_line, None)
        self.text_widget.event_generate("<<Redraw>>")  # ✅ Trigger line number redraw
        self._schedule_draw()

    def _find_block_end(self, start_index):
        lines = self.text_widget.get(start_index, "end-1c").splitlines()
        start_line_no = int(start_index.split(".")[0])
        base_indent = self._get_indent(lines[0])
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "":
                continue
            indent = self._get_indent(line)
            if indent <= base_indent:
                return f"{start_line_no + i}.0"
        return f"{start_line_no + len(lines)}.0"

    def _get_indent(self, line):
        return len(line) - len(line.lstrip(" "))
