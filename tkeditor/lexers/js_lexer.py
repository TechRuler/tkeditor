import re
from tkeditor.lexers.base_lexer import BaseLexer

class JavaScriptLexer(BaseLexer):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor.text
        self.custom_styles: dict = {}

        self.tags = ["keyword", "builtin", "functionName", "className", "method",
                     "attribute", "number", "constant", "string", "template", "comments", "words"]

        self.words = {}

    def add_word_to_highlight(self, word: str, color: str):
        self.words[word] = color
        self.editor.tag_configure(word, **color)

    def set_custom_styles(self, custom_styles: dict):
        self.custom_styles = custom_styles

    def setup_tags(self):
        default_tags = {
            "keyword": {"foreground": "#FF9D00"},
            "builtin": {"foreground": "#F122DA"},
            "functionName": {"foreground": "#C678DD"},
            "className": {"foreground": "#C678DD"},
            "method": {"foreground": "#C678DD"},
            "attribute": {"foreground": "#61AFEF"},
            "number": {"foreground": "#98C379"},
            "constant": {"foreground": "#56B6C2"},
            "string": {"foreground": "#98C379"},
            "template": {"foreground": "#C586C0"},
            "comments": {"foreground": "#5C6370"},
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

        self._keywords_builtins_constants(code, first)
        self._functions_classes(code, first)
        self._attributes(code, first)
        self._strings(code, first)
        self._template_strings(code, first)
        self._comments(code, first)

    def _keywords_builtins_constants(self, code, first):
        keywords = r"\b(?:if|else|return|for|while|do|switch|case|break|continue|function|class|new|try|catch|finally|throw|import|export|default|extends|super|in|instanceof|typeof|void|delete|yield|await|async|with|let|const|var)\b"
        builtins = r"\b(?:console|window|document|Array|Object|Math|Date|String|Number|Boolean|JSON|RegExp|Set|Map|Symbol|Error|Promise|Intl|Reflect)\b"
        constants = r"\b(?:true|false|null|undefined|NaN|Infinity)\b"
        numbers = r"\b\d+(\.\d+)?([eE][+-]?\d+)?\b"

        self._highlight(keywords, "keyword", code, first)
        self._highlight(builtins, "builtin", code, first)
        self._highlight(constants, "constant", code, first)
        self._highlight(numbers, "number", code, first)

    def _functions_classes(self, code, first):
        self._highlight(r"\bfunction\s+([a-zA-Z_$][\w$]*)", "functionName", code, first)
        self._highlight(r"\bclass\s+([a-zA-Z_$][\w$]*)", "className", code, first)
        self._highlight(r"\b([a-zA-Z_$][\w$]*)\s*(?=\()", "method", code, first)

    def _attributes(self, code, first):
        pattern = r"\.([a-zA-Z_$][\w$]*)"
        for match in re.finditer(pattern, code):
            start, end = match.span(1)
            self.editor.tag_add("attribute", f"{first} + {start}c", f"{first} + {end}c")

    def _strings(self, code, first):
        string_pattern = r"(\"(\\.|[^\"])*\"|'(\\.|[^'])*')"
        for match in re.finditer(string_pattern, code):
            start, end = match.span()
            self.editor.tag_add("string", f"{first} + {start}c", f"{first} + {end}c")

    def _template_strings(self, code, first):
        pattern = r"`(?:\\.|[^`])*`"
        for match in re.finditer(pattern, code, re.DOTALL):
            start, end = match.span()
            self.editor.tag_add("template", f"{first} + {start}c", f"{first} + {end}c")

    def _comments(self, code, first):
        # Single-line and multi-line comments
        pattern = r"//.*?$|/\*[\s\S]*?\*/"
        for match in re.finditer(pattern, code, re.MULTILINE):
            start, end = match.span()
            self.editor.tag_add("comments", f"{first} + {start}c", f"{first} + {end}c")

    def _highlight(self, pattern, tag, code, first):
        for match in re.finditer(pattern, code):
            if match.lastindex:
                start_idx = match.start(1)
                end_idx = match.end(1)
            else:
                start_idx = match.start()
                end_idx = match.end()
            self.editor.tag_add(tag, f"{first} + {start_idx}c", f"{first} + {end_idx}c")
