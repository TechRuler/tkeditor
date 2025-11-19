from tkeditor.Lexers.baselexer import BaseLexer
import re

class JSONLexer(BaseLexer):
    name = "json"
    file_extensions = ["json"]

    STRING_RE = re.compile(r'"(\\.|[^"])*"')
    NUMBER_RE = re.compile(r'\b-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?\b')
    BOOLEAN_RE = re.compile(r'\b(true|false|null)\b')

    def lex(self, text):
        tokens = []
        lines = text.split("\n")
        protected = []  # [(line_no, start_col, end_col)]

        # 1) Strings (protected)
        for ln, line in enumerate(lines, start=1):
            for m in self.STRING_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("string", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, e))

        def is_protected(line_no, col):
            for pl, s, e in protected:
                if pl == line_no and s <= col < e:
                    return True
            return False

        # 2) Numbers, booleans, braces, colons, commas
        for ln, line in enumerate(lines, start=1):
            for m in self.NUMBER_RE.finditer(line):
                s, e = m.start(), m.end()
                if not is_protected(ln, s):
                    tokens.append(("number", f"{ln}.{s}", f"{ln}.{e}"))

            for m in self.BOOLEAN_RE.finditer(line):
                s, e = m.start(), m.end()
                if not is_protected(ln, s):
                    tokens.append(("keyword", f"{ln}.{s}", f"{ln}.{e}"))  # boolean/null as keyword

            # operators: { } [ ] : ,
            for i, ch in enumerate(line):
                if ch in "{}[]:," and not is_protected(ln, i):
                    tokens.append(("operator", f"{ln}.{i}", f"{ln}.{i+1}"))

        return tokens
