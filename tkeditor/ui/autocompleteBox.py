from tkinter import Frame, Text
from tkinter.ttk import Treeview, Style
from tkeditor.utils.helper import get_font
import re

WORD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

class DropDown(Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.editor: Text = master.get_text_widget()
        self.style = Style(self)

        self.font = get_font(self.editor.cget("font"))
        self.style.configure("Custom.Treeview", font=self.font)

        self.box = Treeview(self, show="tree", selectmode="browse", style="Custom.Treeview")
        self.box.pack(expand=True, fill="both")


        self.editor.bind("<KeyRelease>", self.show_dropdown, add="+")
        self.box.bind("<Double-1>", self.insert_selection)


    def collect_words(self) -> set:
        """Collect unique words typed in editor"""
       
        return  self.editor.lexer.identifiers


    def show_dropdown(self, event):
        # ignore control keys
        if not event.char or not event.char.isprintable():
            self.place_forget()
            return

        # get current prefix
        index = self.editor.index("insert")
        line = self.editor.get(index + " linestart", index)
        match = re.findall(r"[A-Za-z_][A-Za-z0-9_]*$", line)
        if not match:
            self.place_forget()
            return

        prefix = match[0]

        # collect words
        words = self.collect_words()
        suggestions = sorted([w for w in words if w.startswith(prefix) and w != prefix])

        if not suggestions:
            self.place_forget()
            return

        # display popup
        self.box.delete(*self.box.get_children())
        for w in suggestions:
            self.box.insert("", "end", text=w)

        bbox = self.editor.bbox("insert")
        if not bbox:
            self.place_forget()
            return

        x, y, _, _ = bbox
        self.place_configure(
            x=x, 
            y=(y + self.font.metrics("linespace")), 
            height=self.font.metrics("linespace")*len(suggestions) if len(suggestions) <= 6 else self.font.metrics("linespace")*6
        )
        self.lift()


    def insert_selection(self, event=None):
        selection = self.box.focus()
        if not selection:
            return
        word = self.box.item(selection, "text")

        # delete the current prefix
        index = self.editor.index("insert")
        line = self.editor.get(index + " linestart", index)
        prefix = re.findall(r"[A-Za-z_][A-Za-z0-9_]*$", line)[0]
        self.editor.delete(f"insert-{len(prefix)}c", "insert")

        # insert chosen completion
        self.editor.insert("insert", word)
        self.place_forget()
