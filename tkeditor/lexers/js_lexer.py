import re
from tkeditor.lexers.base_lexer import BaseLexer

class JavaScriptLexer(BaseLexer):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor.text
        self.custom_styles = {}
        self.editor.set_language("javascript")
        self.__tags = [
            "keyword", "builtin", "functionName", "className", "method",
            "attribute", "number", "constant", "string", "comments", "words"
        ]

        self.words = {}

    def style_key(self):
        tag = self.__tags.copy()
        tag.remove("words")
        return tag

    def add_word_to_highlight(self, word: str, color: str):
        self.words[word] = color
        self.editor.tag_configure(word, **color)

    def set_custom_styles(self, custom_styles: dict):
        self.custom_styles = custom_styles

    def setup_tags(self):
        default_tags = {
            "attribute": {"foreground": "#61AFEF"},
            "method": {"foreground": "#C678DD"},
            "functionName": {"foreground": "#C678DD"},
            "builtin": {"foreground": "#F122DA"},
            "className": {"foreground": "#C678DD"},
            "constant": {"foreground": "#98C379"},
            "number": {"foreground": "#98C379"},
            "keyword": {"foreground": "#FF9D00"},
            "comments": {"foreground": "#5C6370"},
            "string": {"foreground": "#98C379"},
        }

        for tag, default_config in default_tags.items():
            merged_config = default_config.copy()
            if tag in self.custom_styles:
                merged_config.update(self.custom_styles[tag])
            self.editor.tag_configure(tag, **merged_config)

    def highlight(self):
        for tag in self.__tags:
            self.editor.tag_remove(tag, '1.0', 'end')

        first_index = self.editor.index("@0,0")
        first = self.editor.index(f"{first_index} -4line")
        last = self.editor.index(f"@0,{self.editor.winfo_height()} +4line")
        code = self.editor.get(first, last)

        for word in self.words:
            self._highlight(fr'\b{word}\b', word, code, first)

        self._attributes(code, first)
        self._highlight_core(code, first)
        self._string(code, first)
        self._comment(code, first)

    def _string(self, code, first):
        string_pattern = r'(".*?"|\'.*?\')'
        for match in re.finditer(string_pattern, code):
            start, end = match.span()
            self.editor.tag_add("string", f"{first} + {start}c", f"{first} + {end}c")

    def _comment(self, code, first):
        comment_pattern = r'//.*?$|/\*.*?\*/'
        for match in re.finditer(comment_pattern, code, re.DOTALL | re.MULTILINE):
            start, end = match.span()
            self.editor.tag_add("comments", f"{first} + {start}c", f"{first} + {end}c")

    def _highlight_core(self, code, first):
        syntax = {
            "keyword": r"\b(const|let|var|if|else|for|while|function|return|switch|case|break|continue|class|extends|super|try|catch|finally|throw|new|in|instanceof|typeof|void|delete|await|async|yield|import|export|default|from|as)\b",
            "builtin": r"\b(Array|Boolean|Date|Error|Function|JSON|Math|Number|Object|Promise|RegExp|String|Symbol|Map|Set|WeakMap|WeakSet|BigInt)\b",
            "functionName": r"\bfunction\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            "className": r"\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            "method": r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\()",
            "number": r"\b\d+(\.\d+)?\b",
            "constant": r"\b(true|false|null|undefined|NaN|Infinity)\b"
        }

        for tag, pattern in syntax.items():
            self._highlight(pattern, tag, code, first)

    def _attributes(self, code, first):
        attribute_pattern = r"\.([a-zA-Z_][a-zA-Z0-9_]*)"
        for match in re.finditer(attribute_pattern, code):
            start, end = match.span(1)
            self.editor.tag_add("attribute", f"{first} + {start}c", f"{first} + {end}c")

    def _highlight(self, pattern, tag, code, first):
        for match in re.finditer(pattern, code):
            if match.lastindex:
                start_idx = match.start(1)
                end_idx = match.end(1)
            else:
                start_idx = match.start()
                end_idx = match.end()
            start = self.editor.index(f"{first} + {start_idx}c")
            end = self.editor.index(f"{first} + {end_idx}c")
            self.editor.tag_add(tag, start, end)
