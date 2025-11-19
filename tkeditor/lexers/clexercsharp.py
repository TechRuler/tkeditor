from tkeditor.Lexers.baselexer import BaseLexer
import re


CSharp_KEYWORDS = {
    "namespace", "using", "class", "struct", "enum", "interface",
    "public", "private", "protected", "internal", "static", "readonly",
    "sealed", "abstract", "override", "virtual", "async", "await",
    "return", "break", "continue", "if", "else", "switch", "case",
    "for", "foreach", "while", "do", "try", "catch", "finally",
    "throw", "new", "var", "int", "float", "double", "string", "char",
    "bool", "object", "dynamic", "true", "false", "null",
}

class CLexerCSharp(BaseLexer):

    name = "csharp"
    file_extensions = ["cs"]

    # --------------------------
    # REGEX PATTERNS
    # --------------------------
    STRING_RE = re.compile(r'"(\\.|[^"])*"')
    CHAR_RE = re.compile(r"'(\\.|[^'])'")
    IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    FUNC_CALL_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    CLASS_DEF_RE = re.compile(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)")

    def lex(self, text):

        tokens = []
        lines = text.split("\n")

        protected = []  # (line, start, end)

        # -----------------------------------
        # 1) STRINGS + COMMENTS
        # -----------------------------------
        for ln, line in enumerate(lines, start=1):

            # string literal
            for m in self.STRING_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("string", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, e))

            # char literal
            for m in self.CHAR_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("string", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, e))

            # single-line comment //
            if "//" in line:
                i = line.index("//")
                tokens.append(("comment", f"{ln}.{i}", f"{ln}.{len(line)}"))
                protected.append((ln, i, len(line)))

        # -----------------------------------
        # helper: check if inside string/comment
        # -----------------------------------
        def is_protected(line_no, col):
            for pl, a, b in protected:
                if pl == line_no and a <= col < b:
                    return True
            return False

        # -----------------------------------
        # 2) IDENTIFIERS / KEYWORDS / FUNCTIONS
        # -----------------------------------
        for ln, line in enumerate(lines, start=1):

            # Class Definition
            for m in self.CLASS_DEF_RE.finditer(line):
                name_start, name_end = m.start(1), m.end(1)
                if not is_protected(ln, name_start):
                    tokens.append(("class", f"{ln}.{name_start}", f"{ln}.{name_end}"))

            # Keywords + identifiers
            for m in self.IDENT_RE.finditer(line):
                s, e = m.start(), m.end()
                if is_protected(ln, s):
                    continue

                word = m.group(0)

                if word in CSharp_KEYWORDS:
                    tokens.append(("keyword", f"{ln}.{s}", f"{ln}.{e}"))
                else:
                    tokens.append(("ident", f"{ln}.{s}", f"{ln}.{e}"))

            # Function call: name(
            for m in self.FUNC_CALL_RE.finditer(line):
                fname = m.group(1)
                s, e = m.start(1), m.end(1)

                if is_protected(ln, s):
                    continue

                if fname in CSharp_KEYWORDS:
                    continue  # do not highlight keywords as functions

                tokens.append(("function", f"{ln}.{s}", f"{ln}.{e}"))

            # operators
            for i, ch in enumerate(line):
                if ch in "{}[]()+-*/%=!<>:;,.&|^~?":
                    if not is_protected(ln, i):
                        tokens.append(("operator", f"{ln}.{i}", f"{ln}.{i+1}"))

        return tokens
