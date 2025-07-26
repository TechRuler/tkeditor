from tkinter import Menu

class ContextMenu:
    def setup_context_menu(self):
        self.bind("<Button-3>", self.popup_menu, add="+")

    def popup_menu(self, event):
        self.popup = Menu(self, tearoff=0)
        self.popup.add_command(label="Cut", command=lambda: self.event_generate("<<Cut>>"))
        self.popup.add_command(label="Copy", command=lambda: self.event_generate("<<Copy>>"))
        self.popup.add_command(label="Paste", command=lambda: self.event_generate("<<Paste>>"))
        self.popup.post(event.x_root, event.y_root)

    def get_popup_menu(self):
        return self.popup
