from tkinter import Frame
from tkeditor.core import CustomText
from tkeditor.features import LineNumber
class Editor(Frame):
    def __init__(self, master, **kwarg):
        super().__init__(master, **{k:v for k, v in kwarg.items() if k in Frame(master).keys()})

        self.line_number = LineNumber(self, **kwarg)
        self.text  = CustomText(self, **kwarg)


        self.line_number.attach(self.text)


        self.line_number.grid(row=0, column=0, sticky='ns')
        self.text.grid(row=0, column=1, sticky='nsew')

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
    def set_lexer(self, lexer_instance):
        """Accept a lexer object and set up highlighting."""
        self.lexer = lexer_instance
        self.lexer.setup_tags()
        self.text.bind("<KeyRelease>", self._on_key_release, add="+")
        self.text.bind("<Configure>", self._on_key_release, add="+")
        self.text.bind("<MouseWheel>", self._on_key_release, add="+")
        self.text.bind("<Button-1>", self._on_key_release, add="+")
        self._on_key_release()

    def apply_lexer_style(self, tag_config):
        if hasattr(self.lexer, "setup_tags"):
            self.lexer.setup_tags(tag_config)
            self.lexer.highlight()


    
    def _on_key_release(self, event=None):
        """Callback to update highlighting after key press."""
        if hasattr(self, 'lexer'):
            self.lexer.highlight()


    def bind(self, sequence=None, func=None, add=None):
        self.text.bind(sequence, func, add)