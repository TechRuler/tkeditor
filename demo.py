from tkeditor import Editor
from tkeditor.lexers import PythonLexer
from tkinter import *

root = Tk()
root.title("Code")
editor = Editor(root, font=("JetBrains Mono",12), bd=0, bg='#2b2b2b', highlightthickness=0,wrap='none', 
                fg='#ffffff', line_number_fg='#ffffff', line_number_bg="#4b4b4b", insertbackground='#ffffff')
editor.pack(expand=True, fill="both")

lexer = PythonLexer(editor)
lexer.set_custom_styles({
    "keyword": {"foreground": "#00FFFF","font":("JetBrains Mono",12,"italic")},
    "comment": {"foreground": "#808080"},
    "string": {"foreground": "#90EE90"},
    "attribute": {"foreground": "steelblue"},
    "method": {"foreground": "#FF00FF"},
    "functionName":{"foreground":"tomato"},
    "className":{"foreground":"gold"}
})
lexer.add_word_to_highlight('self', {"foreground":"#00FFFF"})


editor.set_lexer(lexer)


root.mainloop()
