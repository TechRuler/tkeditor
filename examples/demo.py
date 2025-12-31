import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tkinter as tk
from tkeditor import Editor
from tkeditor.lexers import PythonLexer,Highlighter

root = tk.Tk()
root.geometry("800x500") 
root.title("tkeditor")
editor = Editor(
    root,
    linenumber=True,
    folder_code=True,
    wrap="none",
    font=("Consolas", 12),
)

editor.pack(expand=True, fill="both")


lexer = PythonLexer()

# set custom syntax colors
# method 1
# lexer.set_styles(
#     keyword={"foreground":"tomato"},
#     builtin={"foreground":"steelblue"}
# )
# method 2 
# lexer.set_styles({
#     "keyword":{"foreground":"tomato"},
#     "builtin":{"foreground":"steelblue"}
#     }
# )
# Note you can also use both methods at same time

highlight = Highlighter(editor.get_text_widget(), lexer)
root.mainloop()
