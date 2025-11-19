from tkeditor.Lexers.baselexer import BaseLexer
import re

HTML_KEYWORDS = {
    "html","head","body","title","meta","link","script","style","div","span",
    "h1","h2","h3","h4","h5","h6","p","a","ul","ol","li","table","tr","td","th",
    "form","input","textarea","button","label","select","option","nav","footer","header",
    "section","article","aside","main","figure","figcaption","canvas","svg","video","audio",
    "source","iframe","strong","em","b","i","u","small","big","pre","code","br","hr"
}

class HTMLLexer(BaseLexer):

    name = "html"
    file_extensions = ["html","htm"]

    TAG_RE = re.compile(r"</?[A-Za-z0-9_\-]+")
    ATTR_RE = re.compile(r'\b([a-zA-Z\-:]+)\b(?=\=)')
    STRING_RE = re.compile(r'"[^"]*"|\'[^\']*\'')
    COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
    OPERATOR_CHARS = set("<>/=:")

    def lex(self, text):
        tokens = []
        lines = text.split("\n")
        protected = []  # (line, start, end)

        # -------------------------------
        # 1) Comments and strings
        # -------------------------------
        for ln, line in enumerate(lines, start=1):
            # comments
            for m in self.COMMENT_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("comment", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, e))
            # strings
            for m in self.STRING_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("string", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, e))

        # helper
        def is_protected(line_no, col):
            for pl, a, b in protected:
                if pl == line_no and a <= col < b:
                    return True
            return False

        # -------------------------------
        # 2) Tags, attributes, operators
        # -------------------------------
        for ln, line in enumerate(lines, start=1):
            # tags
            for m in self.TAG_RE.finditer(line):
                s, e = m.start(), m.end()
                if not is_protected(ln, s):
                    tokens.append(("keyword", f"{ln}.{s}", f"{ln}.{e}"))

            # attributes
            for m in self.ATTR_RE.finditer(line):
                s, e = m.start(1), m.end(1)
                if not is_protected(ln, s):
                    tokens.append(("ident", f"{ln}.{s}", f"{ln}.{e}"))

            # operators
            for i, ch in enumerate(line):
                if ch in self.OPERATOR_CHARS:
                    if not is_protected(ln, i):
                        tokens.append(("operator", f"{ln}.{i}", f"{ln}.{i+1}"))

        return tokens
