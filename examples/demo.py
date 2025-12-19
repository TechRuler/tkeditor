import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tkeditor import Editor
from tkeditor.Lexers import PythonLexer,Highlighter,HTMLLexer
from tkinter import *

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
highlight = Highlighter(editor.get_text_widget(), lexer)
root.mainloop()
