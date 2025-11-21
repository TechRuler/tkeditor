class Highlighter:
    def __init__(self, text_widget, lexer):
        self.text = text_widget
        self.lexer = lexer

        # create tags
        self.styles = lexer.get_styles()
        for name, attrs in self.styles.items():
            self.text.tag_configure(name, **attrs)

        self.text.bind("<<Modified>>", self.schedule, add="+")
        self.after_id = None

    def schedule(self, event=None):
        if self.text.edit_modified():
            self.text.edit_modified(False)
            if self.after_id:
                self.text.after_cancel(self.after_id)
            self.after_id = self.text.after(60, self.highlight)

    def highlight(self):
        code = self.text.get("1.0", "end-1c")

        # remove all tags
        for name in self.styles:
            self.text.tag_remove(name, "1.0", "end")

        # apply new tokens
        for token_type, start, end in self.lexer.lex(code):
            self.text.tag_add(token_type, start, end)
