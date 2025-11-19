from tkeditor.Lexers.baselexer import BaseLexer
import re

RUBY_KEYWORDS = {
    "def", "class", "module", "end", "if", "elsif", "else", "unless", "while",
    "for", "in", "do", "break", "next", "redo", "retry", "return", "yield",
    "super", "self", "nil", "true", "false", "and", "or", "not", "then",
    "begin", "rescue", "ensure", "case", "when"
}

class RubyLexer(BaseLexer):
    name = "ruby"
    file_extensions = ["rb"]

    STRING_RE = re.compile(r'(["\'])(?:\\.|(?!\1).)*\1')
    COMMENT_RE = re.compile(r'#.*')
    IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    FUNC_CALL_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*(?=\()")

    def lex(self, text):
        tokens = []
        lines = text.split("\n")
        protected = []  # [(line_no, start_col, end_col)]

        # 1) Strings and comments
        for ln, line in enumerate(lines, start=1):
            for m in self.STRING_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("string", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, e))

            for m in self.COMMENT_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("comment", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, e))

        def is_protected(line_no, col):
            for pl, s, e in protected:
                if pl == line_no and s <= col < e:
                    return True
            return False

        # 2) Keywords, identifiers, functions
        for ln, line in enumerate(lines, start=1):
            for m in self.IDENT_RE.finditer(line):
                s, e = m.start(), m.end()
                if is_protected(ln, s):
                    continue
                word = m.group(0)
                if word in RUBY_KEYWORDS:
                    tokens.append(("keyword", f"{ln}.{s}", f"{ln}.{e}"))
                else:
                    tokens.append(("ident", f"{ln}.{s}", f"{ln}.{e}"))

            for m in self.FUNC_CALL_RE.finditer(line):
                s, e = m.start(1), m.end(1)
                if is_protected(ln, s):
                    continue
                tokens.append(("function", f"{ln}.{s}", f"{ln}.{e}"))

            # operators
            for i, ch in enumerate(line):
                if ch in "{}[]()+-*/%=!<>:;,.&|^~?":
                    if not is_protected(ln, i):
                        tokens.append(("operator", f"{ln}.{i}", f"{ln}.{i+1}"))

        return tokens
