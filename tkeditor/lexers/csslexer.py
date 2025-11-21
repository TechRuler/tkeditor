from tkeditor.Lexers.baselexer import BaseLexer
import re

CSS_PROPERTIES = {
    "color", "background", "font-size", "font-family", "margin", "padding",
    "border", "width", "height", "display", "position", "top", "left",
    "right", "bottom", "flex", "grid", "align-items", "justify-content",
    "text-align", "line-height", "opacity", "overflow", "z-index"
}

class CSSLexer(BaseLexer):
    name = "css"
    file_extensions = ["css"]

    COMMENT_RE = re.compile(r'/\*.*?\*/', re.DOTALL)
    SELECTOR_RE = re.compile(r'^[^{]+(?=\{)')
    PROPERTY_RE = re.compile(r'([a-zA-Z-]+)\s*:')
    VALUE_RE = re.compile(r':\s*([^;]+);')
    OPERATOR_RE = re.compile(r'[{}:;]')

    def lex(self, text):
        tokens = []
        lines = text.split("\n")
        protected = []

        # 1) Comments (protected)
        for ln, line in enumerate(lines, start=1):
            for m in self.COMMENT_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("comment", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, e))

        def is_protected(line_no, col):
            for pl, s, e in protected:
                if pl == line_no and s <= col < e:
                    return True
            return False

        # 2) Process each line
        for ln, line in enumerate(lines, start=1):

            # Selector
            m = self.SELECTOR_RE.match(line)
            if m:
                s, e = m.start(), m.end()
                if not is_protected(ln, s):
                    tokens.append(("selector", f"{ln}.{s}", f"{ln}.{e}"))

            # Properties
            for m in self.PROPERTY_RE.finditer(line):
                s, e = m.start(1), m.end(1)
                prop = m.group(1)
                tokens.append(("property", f"{ln}.{s}", f"{ln}.{e}"))

            # Values
            for m in self.VALUE_RE.finditer(line):
                s, e = m.start(1), m.end(1)
                tokens.append(("value", f"{ln}.{s}", f"{ln}.{e}"))

            # Operators
            for m in self.OPERATOR_RE.finditer(line):
                s, e = m.start(), m.end()
                if not is_protected(ln, s):
                    tokens.append(("operator", f"{ln}.{s}", f"{ln}.{e}"))

        return tokens
