import re

class AutoIndent:
    def setup_auto_indent(self):
        self.bind("<Return>", self.auto_indent, add="+")
        self.bind("<BackSpace>", self.backspace, add="+")

    def set_indentation(self, indent:int):
        """Set the indentation level for auto-indentation."""

        if isinstance(indent, int) and indent >= 0:
            if indent > 0:
                self.indentation = indent
            else:
                raise ValueError("Indentation must be a positive integer.")
        else:
            raise TypeError("Indentation must be an integer.")
        
        
    def auto_indent(self, event):
        """Handle auto-indentation logic."""
        current_line = self.get("insert linestart", "insert")
        match = re.match(r"(\s*)", current_line)
        if match:
            indent = len(match.group(1))
            if self.get('insert -1c wordstart', 'insert').strip() == ":":
                indent += self.indentation
            elif self.get('insert -1c wordstart', 'insert').strip() == "{":
                indent += self.indentation
            self.insert("insert", "\n" + " " * indent)
            self.see('insert')
            self.event_generate("<<Redraw>>")
            return "break"
        self.see('insert')
        
    def backspace(self, event):
        """Handle backspace key press to remove indentation if necessary."""
        current_line = self.get("insert linestart", "insert")
        if current_line.isspace() and not self.tag_ranges("sel"):
            if len(current_line) % self.indentation == 0:
                self.delete("%s-%sc"%("insert", self.indentation), "insert")
                self.event_generate("<<Redraw>>")
                return "break"
        self.event_generate("<<Redraw>>")
