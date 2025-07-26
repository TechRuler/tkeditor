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

    


    def bind(self, sequence=None, func=None, add=None):
        if sequence == "<Key>":
            return super().bind(sequence, func, add="+")
        return super().bind(sequence, func, add=add)
