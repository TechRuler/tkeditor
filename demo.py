from tkeditor import Editor
from tkeditor.lexers import PythonLexer
from tkinter import *

root = Tk()
root.geometry("800x500")
root.title("Code")
editor = Editor(root, font=("Consolas",14), 
                bd=0, bg='#2b2b2b', 
                highlightthickness=0,wrap='none',
                linenumber=True,indentationguide=True,
                fg='#ffffff', line_number_fg='#ffffff', 
                line_number_bg="#2b2b2b", insertbackground='#ffffff')

editor.pack(expand=True, fill="both")



lexer = PythonLexer(editor)



editor.set_lexer(lexer)


root.mainloop()
