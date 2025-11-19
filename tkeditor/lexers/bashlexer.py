from tkeditor.Lexers.baselexer import BaseLexer
import re

BASH_KEYWORDS = {
    "if", "then", "else", "elif", "fi",
    "for", "while", "do", "done",
    "case", "esac", "function", "select", "in", "until", "break", "continue", "return",
}

class BashLexer(BaseLexer):
    name = "bash"
    file_extensions = ["sh", "bash"]

    COMMENT_RE = re.compile(r"#.*")
    STRING_RE = re.compile(r'"(?:\\.|[^"])*"|\'(?:\\.|[^\'])*\'')
    VARIABLE_RE = re.compile(r"\$[A-Za-z_][A-Za-z0-9_]*|\$\{[^\}]+\}|\$\d+")
    FUNC_CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(\)")
    IDENT_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
    OPERATOR_CHARS = set("=+-*/%&|!<>;(){}[]")

    def lex(self, text):
        tokens = []
        lines = text.split("\n")
        protected = []  # (line, start, end)

        # ------------------------
        # 1) Comments & strings
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
        # 2) Variables, keywords, functions, operators
        # ------------------------
        for ln, line in enumerate(lines, start=1):

            # variables
            for m in self.VARIABLE_RE.finditer(line):
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
                if word in BASH_KEYWORDS:
                    tokens.append(("keyword", f"{ln}.{s}", f"{ln}.{e}"))
                else:
                    tokens.append(("ident", f"{ln}.{s}", f"{ln}.{e}"))

            # operators
            for i, ch in enumerate(line):
                if ch in self.OPERATOR_CHARS and not is_protected(ln, i):
                    tokens.append(("operator", f"{ln}.{i}", f"{ln}.{i+1}"))

        return tokens
