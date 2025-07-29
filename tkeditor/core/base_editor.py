from tkinter import Text
from tkeditor.features import Indentations, IndentationGuide
from tkeditor.components import ContextMenu
class CustomText(Text, Indentations):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **{k:v for k, v in kwargs.items() if k in Text(master).keys()})
        self.variables()

        self.context_menu = ContextMenu(self)

        self.setup_auto_indent()        
        self.context_menu.setup_context_menu()
        
        self.indentationguide = IndentationGuide(text=self, color=kwargs.get('indent_line_color','#4b4b4b'))    

        super().bind('<Key>', self.brackets_and_string_complete, add="+")
        super().bind("<Tab>", self._handle_tab, add="+")

        if kwargs.get('indentationguide',False):
            self.indentationguide.set_indentationguide()
    def variables(self):
        self.indentation = 4
        self.tab_width = 4
    def configure(self, **kwargs):
        super().configure(**{k:v for k, v in kwargs.items() if k in Text().keys()})
        if "indentationguide" in kwargs.keys():
            if kwargs.get('indentationguide'):
                self.indentationguide.set_indentationguide()
            else:
                self.indentationguide.remove_indentationguide()
    def brackets_and_string_complete(self, event):
        char = event.char
        brackets = {"[":"]","(":")","{":"}","'":"'",'"':'"'}
        if char in brackets.keys():
            self.mark_gravity('insert','left')
            self.insert('insert', brackets[char])
            self.mark_gravity('insert','right')

    def set_tabWidth(self, width:int):
        """Set the tab width for the editor."""
        if isinstance(width, int) and width >= 0:
            if width > 0:
                self.tab_width = width
            else:
                raise ValueError("Tab width must be a positive integer.")
        else:
            raise TypeError("Tab width must be an integer.")
        
    def _handle_tab(self, event):
        """Handle tab key press for indentation."""
        self.insert("insert", " " * self.tab_width)
        return "break"

    def bind(self, sequence=None, func=None, add=None):
        if sequence == "<Key>":
            return super().bind(sequence, func, add="+")
        return super().bind(sequence, func, add=add)
