from tkeditor import Editor
from tkeditor.Lexers import PythonLexer,Highlighter, CPPLexer
from tkinter import *

root = Tk()
root.geometry("800x500")
root.title("tkeditor")
editor = Editor(root, font=("Fira Code",14), 
                bd=0, bg='#2b2b2b', 
                highlightthickness=0,wrap='none',selectbackground='#264F78',
                linenumber=True,indentationguide=True,folding_code=True,
                fg='#ffffff', line_number_fg='#ffffff', 
                line_number_bg="#2b2b2b", insertbackground='#ffffff',
                folding_arrow_color='#aaa',folding_bg='#2b2b2b',current_line_color='#3a3a3a',)

editor.pack(expand=True, fill="both")



lexer = CPPLexer()
highlight = Highlighter(editor.text, lexer)
root.mainloop()
