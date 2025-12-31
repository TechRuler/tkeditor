import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tkeditor import Editor
from tkeditor.lexers import PythonLexer,Highlighter
from tkinter import Tk

root = Tk()
root.geometry("800x500") 
root.title("tkeditor")
editor = Editor(
    root, 
    font=("Cascadia Code",15), 
    indent_line_color="red", 
    bracket_tracker=True
)

editor.pack(expand=True, fill="both")


lexer = PythonLexer()
lexer.set_styles(
    keyword={"foreground":"tomato"},
    builtin={"foreground":"steelblue"}
)
highlight = Highlighter(editor.get_text_widget(), lexer)
root.mainloop()
