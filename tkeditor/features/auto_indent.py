import re

class AutoIndent:
    def setup_auto_indent(self):
        self.bind("<Return>", self.auto_indent, add="+")
        self.bind("<BackSpace>", self.backspace, add="+")
        self.language = "python"  # default

    def set_language(self, lang: str):
        self.language = lang.lower()

    def set_indentation(self, indent: int):
        if isinstance(indent, int) and indent > 0:
            self.indentation = indent
        else:
            raise ValueError("Indentation must be a positive integer.")

    def auto_indent(self, event):
        current_line = self.get("insert linestart", "insert")
        match = re.match(r"(\s*)", current_line)
        if match:
            indent = len(match.group(1))
            line_text = current_line.strip()

            # Language-specific block starters
            if self.language == "python":
                if line_text.endswith(":"):
                    indent += self.indentation
                elif line_text.endswith("{"):
                    indent += self.indentation


            elif self.language in ("c", "cpp", "java", "javascript", "csharp"):
                if line_text.endswith("{"):
                    indent += self.indentation

            elif self.language in ("html", "xml"):
                if re.match(r"<[^/!][^>]*[^/]?>$", line_text):  # opening tag
                    indent += self.indentation

            elif self.language == "lua":
                if re.search(r"\b(then|do|function)\b$", line_text):
                    indent += self.indentation

            elif self.language == "yaml":
                if line_text.endswith(":"):
                    indent += self.indentation

            self.insert("insert", "\n" + " " * indent)
            self.see("insert")
            self.event_generate("<<Redraw>>")
            return "break"
        self.see("insert")

    def backspace(self, event):
        current_line = self.get("insert linestart", "insert")
        if current_line.isspace() and not self.tag_ranges("sel"):
            if len(current_line) % self.indentation == 0:
                self.delete(f"insert-{self.indentation}c", "insert")
                self.event_generate("<<Redraw>>")
                return "break"
        self.event_generate("<<Redraw>>")
