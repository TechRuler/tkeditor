import tkinter as tk
from tkinter import ttk
from pygments import lex
from pygments.lexers import PythonLexer, CLexer, JavaLexer, HtmlLexer, CssLexer
from pygments.token import Token

# ---------------------
# Configuration
# ---------------------
LANGUAGES = {
    "python": PythonLexer,
    "c": CLexer,
    "java": JavaLexer,
    "html": HtmlLexer,
    "css": CssLexer,
}

TOKEN_COLORS = {
    Token.Keyword: "blue",
    Token.Name.Builtin: "darkorange",
    Token.Name.Function: "darkgreen",
    Token.Comment: "gray",
    Token.String: "green",
    Token.Number: "purple",
    Token.Operator: "red",
    Token.Punctuation: "black",
    Token.Name.Class: "darkcyan",
    Token.Text: "black",
}

# ---------------------
# Helper Functions
# ---------------------
def get_token_color(token):
    """Return color for a token type"""
    for ttype, color in TOKEN_COLORS.items():
        if token in ttype:
            return color
    return "black"

# ---------------------
# Editor Class
# ---------------------
class SyntaxEditor(tk.Frame):
    def __init__(self, master, language="python", **kwargs):
        super().__init__(master)
        self.language = language
        self.lexer_class = LANGUAGES.get(language, PythonLexer)
        self.lexer = self.lexer_class()

        # Text Widget
        self.text = tk.Text(self, wrap="none", undo=True)
        self.text.pack(fill="both", expand=True)
        self.text.bind("<<Modified>>", self.on_modified)

        # Configure scrollbars
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.hsb = tk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        self.text.configure(xscrollcommand=self.hsb.set)
        self.hsb.pack(side="bottom", fill="x")

        # Initialize tags
        for token, color in TOKEN_COLORS.items():
            self.text.tag_configure(str(token), foreground=color)

        self.text.edit_modified(False)

    def on_modified(self, event=None):
        if self.text.edit_modified():
            self.highlight()
            self.text.edit_modified(False)

    def highlight(self):
        """Highlight the whole text"""
        code = self.text.get("1.0", "end-1c")
        self.text.tag_remove("all", "1.0", "end")

        index = "1.0"
        for token, value in lex(code, self.lexer):
            if not value:
                continue

            # Compute end index
            end_index = self.text.index(f"{index} + {len(value)}c")

            # Find first matching token color
            applied = False
            for ttype, color in TOKEN_COLORS.items():
                # Check if token is child of ttype
                if token == ttype or token in ttype:
                    self.text.tag_add(str(ttype), index, end_index)
                    applied = True
                    break

            # Fallback to black if no match
            if not applied:
                self.text.tag_add("Token.Text", index, end_index)

            index = end_index



# ---------------------
# Main Application
# ---------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("TkEditor - Multi-Language Syntax Highlighting")
    root.geometry("800x600")

    editor = SyntaxEditor(root, language="python")
    editor.pack(fill="both", expand=True)

    # Example code
    example_code = '''\
def hello(name):
    # Print greeting
    print(f"Hello, {name}!")

class Person:
    pass
'''
    editor.text.insert("1.0", example_code)
    editor.highlight()

    root.mainloop()
