from tkeditor.Lexers.baselexer import BaseLexer
import re

class YAMLLexer(BaseLexer):
    name = "yaml"
    file_extensions = ["yml", "yaml"]

    STRING_RE = re.compile(r'"(\\.|[^"])*"|\'(\\.|[^\'])*\'')
    NUMBER_RE = re.compile(r'\b-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?\b')
    BOOLEAN_RE = re.compile(r'\b(true|false|null|yes|no)\b', re.IGNORECASE)
    KEY_RE = re.compile(r'^[ \t]*([A-Za-z0-9_/-]+)\s*:')

    def lex(self, text):
        tokens = []
        lines = text.split("\n")
        protected = []  # (line, start, end)

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

        # 2) Numbers, booleans, keys
        for ln, line in enumerate(lines, start=1):
            # keys
            m = self.KEY_RE.match(line)
            if m:
                s, e = m.start(1), m.end(1)
                if not is_protected(ln, s):
                    tokens.append(("keyword", f"{ln}.{s}", f"{ln}.{e}"))  # keys as keyword

            # numbers
            for m in self.NUMBER_RE.finditer(line):
                s, e = m.start(), m.end()
                if not is_protected(ln, s):
                    tokens.append(("number", f"{ln}.{s}", f"{ln}.{e}"))

            # booleans
            for m in self.BOOLEAN_RE.finditer(line):
                s, e = m.start(), m.end()
                if not is_protected(ln, s):
                    tokens.append(("keyword", f"{ln}.{s}", f"{ln}.{e}"))

            # comments
            if "#" in line:
                idx = line.index("#")
                if not is_protected(ln, idx):
                    tokens.append(("comment", f"{ln}.{idx}", f"{ln}.{len(line)}"))

            # symbols: - (for list items)
            for i, ch in enumerate(line):
                if ch in "-?[]{}:,|" and not is_protected(ln, i):
                    tokens.append(("operator", f"{ln}.{i}", f"{ln}.{i+1}"))

        return tokens
