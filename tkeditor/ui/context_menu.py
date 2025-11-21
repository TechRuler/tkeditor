from tkinter import Menu

class ContextMenu:
    def __init__(self, text):
        self.text = text
        self.popup = Menu(self.text, tearoff=0)
        
        self.popup.add_command(label="Cut", command=self._cut)
        self.popup.add_command(label="Copy", command=self._copy)
        self.popup.add_command(label="Paste", command=self._paste)
        
        # self.setup_context_menu()

    def _cut(self):
        self.text.event_generate("<<Cut>>")
        self.popup.unpost()

    def _copy(self):
        self.text.event_generate("<<Copy>>")
        self.popup.unpost()

    def _paste(self):
        self.text.event_generate("<<Paste>>")
        self.popup.unpost()

    def setup_context_menu(self):
        self.text.bind("<Button-3>", self.popup_menu, add="+")

    def popup_menu(self, event):
        self.popup.post(event.x_root, event.y_root)

    def get_popup_menu(self):
        return self.popup
