from tkinter import Canvas, TclError
from tkeditor.utils import get_font
class FoldingCode(Canvas):
    def __init__(self, master=None, **kwargs):
        Allowed_keys = Canvas(master).keys()
        super().__init__(master, **{k: v for k, v in kwargs.items() if k in Allowed_keys})
        self.configure(
            width=kwargs.get('foldingboxwidth', 20),
            bg=kwargs.get('folding_bg', self.cget('background') or self.cget('bg')),
            highlightthickness=0
        )
        self.text_widget = None
        self.folded_blocks = {}  
        self.tag_prefix = "folded_"
        self.font = get_font(kwargs.get('font', ('Consolas', 14)))
        self.fg = kwargs.get('folding_arrow_color', kwargs.get('fg', '#000000'))
        self.width = kwargs.get('width')
        
    def set_color(self, color):
        """Set the color for folding code."""
        self.fg = color
        self.itemconfig("folding_line", fill=color)
    def attach(self, text_widget):
        self.text_widget = text_widget
        # for event in ("<Configure>", "<KeyRelease>", "<MouseWheel>", "<ButtonRelease-1>"):
        #     self.text_widget.bind(event, self._schedule_draw, add="+")
        # self.bind("<Button-1>", self._on_click)
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
            line_no_int = int(lineno)
            is_hidden = False
            for start, end in self.folded_blocks.items():
                if int(start) < line_no_int < int(end):
                    is_hidden = True
                    break
            if is_hidden:
                index = self.text_widget.index(f"{index}+1line")
                continue

            line_text = self.text_widget.get(f"{lineno}.0", f"{lineno}.end")

            x = 5  # Gutter margin

            # Detect foldable lines (you can expand this)
            
            if line_text.strip() and (line_text.strip().endswith(":") or self._has_block(int(lineno))):
                folded = lineno in self.folded_blocks
                try:
                    # test if font supports arrow
                    symbol = "❯" if folded else "∨"
                except:
                    symbol = "+" if folded else "-"
                self.create_text(x, y, text=symbol, anchor="nw", font=self.font, fill=self.fg, tags=("folding_line", f"line_{lineno}"))

            index = self.text_widget.index(f"{index}+1line")
        # Adjust gutter width if needed
        required_width = 1 * self.font.measure("M") + 10
        if required_width != self.width:
            self.width = required_width
            self.config(width=self.width)
    def _has_block(self, line_number):
        """Return True if the next line is more indented than this one"""
        current_line = self.text_widget.get(f"{line_number}.0", f"{line_number}.end")
        base_indent = self._get_indent(current_line)

        # Check next few lines for indentation
        for offset in range(1, 10):  # Max 10 lines lookahead
            try:
                next_line = self.text_widget.get(f"{line_number + offset}.0", f"{line_number + offset}.end")
            except TclError:
                return False
            if not next_line.strip():
                continue
            if self._get_indent(next_line) > base_indent:
                return True
            else:
                return False
        return False

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
        self.text_widget.event_generate("<<Redraw>>")  
        self._schedule_draw()

    def _unfold_block(self, start_line):
        tag = self.tag_prefix + start_line
        self.text_widget.tag_remove(tag, f"{start_line}.0", f"{self.folded_blocks[start_line]}.end")
        self.folded_blocks.pop(start_line, None)
        self.text_widget.event_generate("<<Redraw>>")  
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
