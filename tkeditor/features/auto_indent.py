from tkinter import Frame
import re

class Indentations:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.setup_auto_indent()
        self.indentation = 4
        
    def setup_auto_indent(self):
        self.text_widget.bind("<Return>", self.auto_indent, add="+")
        self.text_widget.bind("<Control-Return>", self.escape_line, add="+")
        self.text_widget.bind("<BackSpace>", self.backspace, add="+")
        self.language = "python"  # default

    def set_language(self, lang: str):
        self.language = lang.lower()

    def set_indentation(self, indent: int):
        if isinstance(indent, int) and indent > 0:
            self.indentation = indent
        else:
            raise ValueError("Indentation must be a positive integer.")

    def auto_indent(self, event):
        current_line = self.text_widget.get("insert linestart", "insert")
        match = re.match(r"(\s*)", current_line)
        if match:
            indent = len(match.group(1))
            line_text = current_line.strip()

            # Language-specific block starters
            if self.language == "python":
                if line_text.endswith(":"):
                    indent += self.indentation
                

            elif self.language in ("html", "xml"):
                if re.match(r"<[^/!][^>]*[^/]?>$", line_text):  
                    indent += self.indentation

            elif self.language == "lua":
                if re.search(r"\b(then|do|function)\b$", line_text):
                    indent += self.indentation

            elif self.language == "yaml":
                if line_text.endswith(":"):
                    indent += self.indentation
            if line_text.endswith("{") or line_text.endswith("(") or line_text.endswith("["):
                current_indent = indent
                indent += self.indentation
                self.text_widget.insert("insert", "\n" + " " * indent)
                self.text_widget.mark_gravity('insert', 'left')
                self.text_widget.insert("insert", "\n" + " " * current_indent)
                self.text_widget.mark_gravity('insert', 'right')
            else:
                self.text_widget.insert("insert", "\n" + " " * indent)
            self.text_widget.see("insert")
            self.text_widget.event_generate("<<Redraw>>")
            return "break"
        self.see("insert")
    def escape_line(self, event):
        current_line = self.text_widget.get("insert linestart", "insert lineend")
        match = re.match(r"(\s*)", current_line)
        if not match:
            return

        indent = len(match.group(1))
        line_text = current_line.strip()
        language = self.language.lower()

        # Block starters and indent rules
        increase_indent = False
        if language == "python":
            increase_indent = line_text.endswith(":") or ("{" in line_text and not "}" in line_text)
        elif language in ("c", "cpp", "java", "javascript", "csharp"):
            increase_indent = "{" in line_text and not line_text.startswith("}")
        elif language in ("html", "xml"):
            increase_indent = re.match(r"<[^/!][^>]*[^/]?>$", line_text) is not None
        elif language == "lua":
            increase_indent = re.search(r"\b(then|do|function)\b$", line_text) is not None
        elif language == "yaml":
            increase_indent = line_text.endswith(":")

        if increase_indent:
            indent += self.indentation

        # Clean insert logic
        line_content = self.text_widget.get("insert", "insert lineend")
        self.text_widget.delete("insert", "insert lineend")
        self.text_widget.insert("insert", line_content + "\n" + " " * indent)
        self.text_widget.see("insert")
        self.text_widget.event_generate("<<Redraw>>")

        return "break"


    def backspace(self, event):
        current_line = self.text_widget.get("insert linestart", "insert")
        if current_line.isspace() and not self.text_widget.tag_ranges("sel"):
            if len(current_line) % self.indentation == 0:
                self.text_widget.delete(f"insert-{self.indentation}c", "insert")
                self.text_widget.event_generate("<<Redraw>>")
                return "break"
        self.text_widget.event_generate("<<Redraw>>")


class IndentationGuide:
    def __init__(self, text, color=None):
        self.text = text
        self.color = color if color else '#4b4b4b'
        self.indent_lines = []
    def set_color(self, color):
        """Set the color for indentation guide."""
        self.color = color
        for frame in self.indent_lines:
            frame.config(background=color)
    def set_indentationguide(self):
        self.text.original_yview = self.text.yview
        self.text.yview = self.yview_wrapper
        self.text.original_xview = self.text.xview
        self.text.xview = self.xview_wrapper
        self._indent_guide_binds = []
        self._indent_guide_binds.append(self.text.bind("<KeyRelease>", self.schedule_draw, add="+"))
        self._indent_guide_binds.append(self.text.bind("<MouseWheel>", self.schedule_draw, add="+"))
        self._indent_guide_binds.append(self.text.bind("<Configure>", self.schedule_draw, add="+"))
        self._indent_guide_binds.append(self.text.bind("<ButtonRelease-1>", self.schedule_draw, add="+"))

    def remove_indentationguide(self):
        self.text.original_yview = self.text.yview
        self.text.original_xview = self.text.xview
        events = ["<KeyRelease>", "<MouseWheel>", "<Configure>", "<ButtonRelease-1>"]
        for event, bind_id in zip(events, getattr(self, "_indent_guide_binds", [])):
            if bind_id:
                self.text.unbind(event, bind_id)
        self._indent_guide_binds = []

    def schedule_draw(self, event=None):
        self.text.after_idle(self.draw_indent)

    def yview_wrapper(self, *args):
        self.text.original_yview(*args)
        self.schedule_draw()

    def xview_wrapper(self, *args):
        self.text.original_xview(*args)
        self.schedule_draw()

    def draw_indent(self):
        for frame in self.indent_lines:
            frame._used = False

        first = self.text.index("@0,0")
        first_index = int(first.split('.')[0])
        last = self.text.index(f"@0,{self.text.winfo_height()} +1line")
        visible_text = self.text.get(first, last)

        frame_index = 0
        prev_indent_levels = 0
        for line_no, line in enumerate(visible_text.splitlines(), start=first_index):
            if line.strip() == "":
                indent_levels = prev_indent_levels  # Use previous indent
            else:
                match = re.match(r'^\s+', line)
                if match:
                    indent = match.group()
                    indent_width = 4
                    indent_levels = len(indent.replace('\t', ' ' * indent_width)) // indent_width
                    prev_indent_levels = indent_levels
                else:
                    indent_levels = 0
                    prev_indent_levels = 0

            for i in range(indent_levels):
                char_index = f"{line_no}.{i * 4}"
                bbox = self.text.bbox(char_index)
                if bbox:
                    x, y, width, height = bbox
                    if frame_index < len(self.indent_lines):
                        frame = self.indent_lines[frame_index]
                    else:
                        frame = Frame(self.text, background=self.color)
                        self.indent_lines.append(frame)
                    frame.place(x=x, y=y, width=2, height=height)
                    frame._used = True
                    frame_index += 1

        for frame in self.indent_lines[frame_index:]:
            frame.place_forget()
