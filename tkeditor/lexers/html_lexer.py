import re
from tkeditor.lexers.base_lexer import BaseLexer

class HTMLLexer(BaseLexer):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor.text
        self.custom_styles: dict = {}

        self.tags = ["tag", "attribute", "string", "comment", "doctype", "words"]
        self.words = {}

    def add_word_to_highlight(self, word: str, color: str):
        self.words[word] = color
        self.editor.tag_configure(word, **color)

    def set_custom_styles(self, custom_styles: dict):
        self.custom_styles = custom_styles

    def setup_tags(self):
        default_tags = {
            "tag": {"foreground": "#E06C75"},
            "attribute": {"foreground": "#61AFEF"},
            "string": {"foreground": "#98C379"},
            "comment": {"foreground": "#5C6370",},
            "doctype": {"foreground": "#C678DD"},
        }

        for tag, default_config in default_tags.items():
            merged_config = default_config.copy()
            if tag in self.custom_styles:
                merged_config.update(self.custom_styles[tag])
            self.editor.tag_configure(tag, **merged_config)

    def highlight(self):
        for tag in self.tags:
            self.editor.tag_remove(tag, '1.0', 'end')

        first_index = self.editor.index("@0,0")
        first = self.editor.index(f"{first_index} -4line")
        last = self.editor.index(f"@0,{self.editor.winfo_height()} +4line")
        code = self.editor.get(first, last)

        for word in self.words:
            self._highlight(fr'\b{word}\b', word, code, first)

        self._highlight(r'<!--.*?-->', "comment", code, first)
        self._highlight(r'<!DOCTYPE[^>]+>', "doctype", code, first)
        self._highlight(r'</?[a-zA-Z][\w\-]*', "tag", code, first)
        self._highlight(r'\b[a-zA-Z_:][\w\-:]*\s*=', "attribute", code, first)
        self._highlight(r'"[^"]*"|\'[^\']*\'', "string", code, first)

    def _highlight(self, pattern, tag, code, first):
        for match in re.finditer(pattern, code, re.DOTALL):
            start = match.start()
            end = match.end()
            self.editor.tag_add(tag, f"{first} + {start}c", f"{first} + {end}c")
