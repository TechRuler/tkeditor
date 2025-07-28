from tkinter import Text
from tkeditor.features.auto_indent import AutoIndent
from tkeditor.features.tab_handler import TabHandler
from tkeditor.features.context_menu import ContextMenu
from tkeditor.core.init_config import Config
class CustomText(Text, AutoIndent, TabHandler, ContextMenu, Config):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **{k:v for k, v in kwargs.items() if k in Text(master).keys()})

        self.setup_config()           
        self.setup_auto_indent()      
        self.setup_tab_handler()      
        self.setup_context_menu()     

        super().bind('<Key>', self.brackets_and_string_complete, add="+")

    
    def brackets_and_string_complete(self, event):
        char = event.char
        brackets = {"[":"]","(":")","{":"}","'":"'",'"':'"'}
        if char in brackets.keys():
            self.mark_gravity('insert','left')
            self.insert('insert', brackets[char])
            self.mark_gravity('insert','right')


    def bind(self, sequence=None, func=None, add=None):
        if sequence == "<Key>":
            return super().bind(sequence, func, add="+")
        return super().bind(sequence, func, add=add)
