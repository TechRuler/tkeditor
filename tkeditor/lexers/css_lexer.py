import re
from tkeditor.lexers.base_lexer import BaseLexer

class CSSLexer(BaseLexer):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor.text
        self.custom_styles: dict = {}

        self.tags = ["selector", "property", "value", "number", "string", "comment", "important", "words"]
        self.words = {}

    def add_word_to_highlight(self, word: str, color: str):
        self.words[word] = color
        self.editor.tag_configure(word, **color)

    def set_custom_styles(self, custom_styles: dict):
        self.custom_styles = custom_styles

    def setup_tags(self):
        default_tags = {
            "selector": {"foreground": "#C678DD"},
            "property": {"foreground": "#61AFEF"},
            "value": {"foreground": "#98C379"},
            "important": {"foreground": "#E06C75"},
            "number": {"foreground": "#D19A66"},
            "string": {"foreground": "#98C379"},
            "comment": {"foreground": "#5C6370"},
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

        self._highlight(r'/\*.*?\*/', "comment", code, first)
        self._highlight(r'"[^"\n]*"|\'[^\'\n]*\'', "string", code, first)
        self._highlight(r'#[\w\-]+|\.[\w\-]+|\b[a-zA-Z][\w\-]*\s*{', "selector", code, first)
        self._highlight(r'\b[\w\-]+\s*:', "property", code, first)
        self._highlight(r':\s*[^;{}]+', "value", code, first)
        self._highlight(r'\b\d+(\.\d+)?(px|em|rem|%)?', "number", code, first)
        self._highlight(r'!important', "important", code, first)

    def _highlight(self, pattern, tag, code, first):
        for match in re.finditer(pattern, code, re.DOTALL):
            start = match.start()
            end = match.end()
            self.editor.tag_add(tag, f"{first} + {start}c", f"{first} + {end}c")
