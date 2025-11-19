from tkeditor.Lexers.baselexer import BaseLexer
import re


JS_KEYWORDS = {
    "let","const","var",
    "function","return","class","extends","new",
    "if","else","switch","case","break","continue",
    "for","while","do",
    "import","from","export","default",
    "try","catch","finally","throw",
    "true","false","null","undefined",
}


class JavaScriptLexer(BaseLexer):

    name = "javascript"
    file_extensions = ["js", "mjs", "jsx"]

    STRING_RE = re.compile(r"""(["'`])((?:\\.|(?!\1).)*)\1""")
    IDENT_RE = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")
    FUNC_CALL_RE = re.compile(r"([A-Za-z_$][A-Za-z0-9_$]*)\s*\(")
    CLASS_RE = re.compile(r"class\s+([A-Za-z_$][A-Za-z0-9_$]*)")

    def lex(self, text):

        tokens = []
        lines = text.split("\n")

        protected = []   # list of (line, start_col, end_col)

        # ---------------------------------
        # 1) Capture strings + comments first
        # ---------------------------------
        for ln, line in enumerate(lines, start=1):

            # ----- strings -----
            for m in self.STRING_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("string", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, e))

            # ----- comments // -----
            if "//" in line:
                idx = line.index("//")
                tokens.append(("comment", f"{ln}.{idx}", f"{ln}.{len(line)}"))
                protected.append((ln, idx, len(line)))

        # ---------------------------------
        # helper: check if inside protected
        # ---------------------------------
        def is_protected(line, col):
            for pl, a, b in protected:
                if pl == line and a <= col < b:
                    return True
            return False

        # ---------------------------------
        # 2) Now identifiers, keywords, class, functions
        # ---------------------------------
        for ln, line in enumerate(lines, start=1):

            for m in self.IDENT_RE.finditer(line):
                s, e = m.start(), m.end()
                if is_protected(ln, s):
                    continue

                word = m.group(0)
                if word in JS_KEYWORDS:
                    tokens.append(("keyword", f"{ln}.{s}", f"{ln}.{e}"))
                else:
                    tokens.append(("ident", f"{ln}.{s}", f"{ln}.{e}"))

            # ----- class Foo -----
            for m in self.CLASS_RE.finditer(line):
                s, e = m.start(1), m.end(1)
                if not is_protected(ln, s):
                    tokens.append(("class", f"{ln}.{s}", f"{ln}.{e}"))

            # ----- funcName( -----
            for m in self.FUNC_CALL_RE.finditer(line):
                fname = m.group(1)
                s, e = m.start(1), m.end(1)

                if is_protected(ln, s):  
                    continue
                if fname in JS_KEYWORDS:
                    continue

                tokens.append(("function", f"{ln}.{s}", f"{ln}.{e}"))

            # ----- operators -----
            for i, ch in enumerate(line):
                if ch in "{}[]()+-*/%=!<>:;,.":
                    if not is_protected(ln, i):
                        tokens.append(("operator", f"{ln}.{i}", f"{ln}.{i+1}"))

        return tokens
