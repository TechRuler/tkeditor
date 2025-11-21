from tkeditor.Lexers.baselexer import BaseLexer
import re

class XMLLexer(BaseLexer):
    name = "xml"
    file_extensions = ["xml", "xhtml", "svg"]

    # Patterns
    TAG_RE = re.compile(r'</?([A-Za-z0-9:_-]+)')
    ATTR_RE = re.compile(r'([A-Za-z0-9:_-]+)\s*=')
    STRING_RE = re.compile(r'"(\\.|[^"])*"|\'(\\.|[^\'])*\'')
    COMMENT_RE = re.compile(r'<!--(.*?)-->')

    def set_style(self, style:dict) -> dict:
        self.style = style

    def lex(self, text):
        tokens = []
        lines = text.split("\n")
        protected = []  # (line, start, end)

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

        # 2) Tags, attributes, strings
        for ln, line in enumerate(lines, start=1):
            # strings
            for m in self.STRING_RE.finditer(line):
                s, e = m.start(), m.end()
                if not is_protected(ln, s):
                    tokens.append(("string", f"{ln}.{s}", f"{ln}.{e}"))
                    protected.append((ln, s, e))

            # tags
            for m in self.TAG_RE.finditer(line):
                s, e = m.start(1), m.end(1)
                if not is_protected(ln, s):
                    tokens.append(("tag", f"{ln}.{s}", f"{ln}.{e}"))

            # attributes
            for m in self.ATTR_RE.finditer(line):
                s, e = m.start(1), m.end(1)
                if not is_protected(ln, s):
                    tokens.append(("attribute", f"{ln}.{s}", f"{ln}.{e}"))

            # operators: < > / = 
            for i, ch in enumerate(line):
                if ch in "<>/=" and not is_protected(ln, i):
                    tokens.append(("operator", f"{ln}.{i}", f"{ln}.{i+1}"))

        return tokens
