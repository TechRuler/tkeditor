from tkinter import Text
from tkeditor.core.auto_indent import Indentations, IndentationGuide
from tkeditor.core.bracket_match import BracketTracker
class CustomText(Text):
    def __init__(self, master=None, **kwargs):
        Allowed_keys = Text(master).keys()
        super().__init__(master, **{k:v for k, v in kwargs.items() if k in Allowed_keys})
        self.tab_width = 4

        
        self.indent = Indentations(self)
        self.indentationguide = IndentationGuide(text=self, color=kwargs.get('indent_line_color','#4b4b4b'))    
        self.current_linecolor = kwargs.get('current_line_color', '#eee')
        self.tag_configure("current_line", background=self.current_linecolor)

        self.set_current_line_color()

        if kwargs.get('indentationguide',False):
            self.indentationguide.set_indentationguide()
        
        self.bracket_tracker = BracketTracker(self, kwargs.get('bracket_tracker_color','lightblue'))

        # self.Events()

    def Events(self):
        """Bind events to the text widget."""
        for key in ["[", "{", "(", "]", "}", ")", "'", '"']:
            super().bind(f"<Key-{key}>", self.brackets_and_string_complete, add="+")
        # super().bind('<Key>', self.brackets_and_string_complete, add="+")
        super().bind("<Tab>", self._handle_tab, add="+")
        super().bind("<Button-1>", self.set_current_line_color, add="+")
        super().bind("<Key>", self.set_current_line_color, add="+")
        super().bind("<B1-Motion>", lambda e: self.tag_remove('current_line','1.0','end'), add="+")
        
    def set_language(self, lang: str):
        self.indent.set_language(lang)

    def set_indentation(self, indent: int):
        self.indent.set_indentation(indent)

    
        
    def set_current_line_color(self, event=None):
        """Set the color for the current line in the editor."""
        def task():
            if not self.tag_ranges("sel"):
                self.tag_remove("current_line", "1.0", "end")
                self.tag_add("current_line", "insert linestart", "insert lineend+1c")
            else:
                self.tag_remove("current_line", "1.0", "end")
            self.tag_lower("current_line", "sel")
            self.tag_lower("current_line", "BracketTracker")

        self.after_idle(task)


    def configure(self, **kwargs):
        super().configure(**{k:v for k, v in kwargs.items() if k in Text().keys()})
        if "indentationguide" in kwargs.keys():
            if kwargs.get('indentationguide'):
                self.indentationguide.set_indentationguide()
            else:
                self.indentationguide.remove_indentationguide()

    def brackets_and_string_complete(self, event):
        self.set_current_line_color()
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
        self.set_current_line_color(event)
        return "break"

    def bind(self, sequence=None, func=None, add=None):
        if sequence == "<Key>":
            return super().bind(sequence, func, add="+")
        return super().bind(sequence, func, add=add)
    
    def get_all_content(self):
        return self.get("1.0", "end")
    
    def get_visible_content(self):
        first_line = self.index("@0,0")
        last_line = self.index(f"@0,{self.winfo_height()}")
        return self.get(first_line, last_line)

    