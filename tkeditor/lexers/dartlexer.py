from tkeditor.Lexers.baselexer import BaseLexer
import re

DART_KEYWORDS = {
    "abstract","as","assert","async","await","break","case","catch",
    "class","const","continue","covariant","default","deferred","do",
    "dynamic","else","enum","export","extends","extension","external",
    "factory","false","final","finally","for","Function","get","hide",
    "if","implements","import","in","interface","is","late","library",
    "mixin","new","null","on","operator","part","required","return",
    "set","show","static","super","switch","sync","this","throw","true",
    "try","typedef","var","void","while","with","yield"
}

class DartLexer(BaseLexer):
    name = "dart"
    file_extensions = ["dart"]

    # Regexes
    STRING_RE = re.compile(r"'''[\s\S]*?'''|\"\"\"[\s\S]*?\"\"\"|'(?:\\.|[^'])*'|\"(?:\\.|[^\"])*\"")
    COMMENT_RE = re.compile(r"//.*|/\*[\s\S]*?\*/")
    NUMBER_RE = re.compile(r"\b\d+(\.\d+)?\b")
    FUNC_CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(?=\()")
    IDENT_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
    OPERATORS = set("=+-*/%&|!<>:;.,?(){}[]~^")

    def lex(self, text):
        tokens = []
        lines = text.split("\n")
        protected = []  # list of (line, start, end) for string/comment spans

        # ------------------------
        # 1) Strings & Comments
        # ------------------------
        for ln, line in enumerate(lines, start=1):
            for m in self.COMMENT_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("comment", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, e))
            for m in self.STRING_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("string", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, e))

        def is_protected(line_no, col):
            for pl, a, b in protected:
                if pl == line_no and a <= col < b:
                    return True
            return False

        # ------------------------
        # 2) Numbers, identifiers, keywords, functions, operators
        # ------------------------
        for ln, line in enumerate(lines, start=1):

            # numbers
            for m in self.NUMBER_RE.finditer(line):
                s, e = m.start(), m.end()
                if not is_protected(ln, s):
                    tokens.append(("number", f"{ln}.{s}", f"{ln}.{e}"))

            # function calls
            for m in self.FUNC_CALL_RE.finditer(line):
                fname = m.group(1)
                s, e = m.start(1), m.end(1)
                if not is_protected(ln, s):
                    tokens.append(("function", f"{ln}.{s}", f"{ln}.{e}"))

            # identifiers and keywords
            for m in self.IDENT_RE.finditer(line):
                s, e = m.start(), m.end()
                if is_protected(ln, s):
                    continue
                word = m.group(0)
                if word in DART_KEYWORDS:
                    tokens.append(("keyword", f"{ln}.{s}", f"{ln}.{e}"))
                else:
                    tokens.append(("ident", f"{ln}.{s}", f"{ln}.{e}"))

            # operators
            for i, ch in enumerate(line):
                if ch in self.OPERATORS and not is_protected(ln, i):
                    tokens.append(("operator", f"{ln}.{i}", f"{ln}.{i+1}"))

        return tokens
