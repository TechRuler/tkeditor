from tkeditor.lexers.baselexer import BaseLexer
import re


C_KEYWORDS = {
    "int","char","float","double","void","long","short",
    "for","while","do","if","else","switch","case","return","break","continue",
    "struct","typedef","enum","union","sizeof","static","const","volatile",
    "signed","unsigned","goto",
}


class CLexer(BaseLexer):

    name = "c"
    file_extensions = ["c", "h"]

    STRING_RE = re.compile(r'"(\\.|[^"])*"')
    CHAR_RE = re.compile(r"'(\\.|[^'])'")
    IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    FUNC_CALL_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    PREPROCESSOR_RE = re.compile(r"#\s*[A-Za-z_][A-Za-z0-9_]*")

    def lex(self, text):

        tokens = []
        lines = text.split("\n")

        protected = []   # (line, start, end)

        # -----------------------------------
        # 1) Strings + comments (protected)
        # -----------------------------------
        for ln, line in enumerate(lines, start=1):

            # string literals
            for m in self.STRING_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("string", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, e))

            # char literals
            for m in self.CHAR_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("string", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, e))
            
            # preprocessor directives
            m = self.PREPROCESSOR_RE.match(line)
            if m:
                s, e = m.start(), m.end()
                tokens.append(("preprocessor", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, len(line)))

            # comments //
            if "//" in line:
                i = line.index("//")
                tokens.append(("comment", f"{ln}.{i}", f"{ln}.{len(line)}"))
                protected.append((ln, i, len(line)))
            
        # -----------------------------------
        # helper: check if inside protected
        # -----------------------------------
        def is_protected(line_no, col):
            for pl, a, b in protected:
                if pl == line_no and a <= col < b:
                    return True
            return False
        #numbers
        for m in re.finditer(r'\b\d+(\.\d+)?\b', line):
            s, e = m.start(), m.end()
            if not is_protected(ln, s):
                tokens.append(("number", f"{ln}.{s}", f"{ln}.{e}"))
        # -----------------------------------
        # 2) IDENT, KEYWORD, FUNCTION, OPERATOR
        # -----------------------------------
        for ln, line in enumerate(lines, start=1):

            # identifiers + keywords
            for m in self.IDENT_RE.finditer(line):
                s, e = m.start(), m.end()

                if is_protected(ln, s):
                    continue

                word = m.group(0)

                if word in C_KEYWORDS:
                    tokens.append(("keyword", f"{ln}.{s}", f"{ln}.{e}"))
                else:
                    tokens.append(("ident", f"{ln}.{s}", f"{ln}.{e}"))

            # function call: name(
            for m in self.FUNC_CALL_RE.finditer(line):
                fname = m.group(1)
                s, e = m.start(1), m.end(1)

                if is_protected(ln, s):
                    continue

                if fname in C_KEYWORDS:
                    continue

                tokens.append(("function", f"{ln}.{s}", f"{ln}.{e}"))

            # operators
            for i, ch in enumerate(line):
                if ch in "{}[]()+-*/%=!<>:;,.&|^~?":
                    if not is_protected(ln, i):
                        tokens.append(("operator", f"{ln}.{i}", f"{ln}.{i+1}"))

        return tokens
