from tkeditor.Lexers.baselexer import BaseLexer
import re

CPP_KEYWORDS = {
    "auto","bool","break","case","catch","char","class","const","constexpr",
    "continue","decltype","default","delete","do","double","else","enum",
    "explicit","extern","false","float","for","friend","goto","if","inline",
    "int","long","mutable","namespace","new","noexcept","nullptr","operator",
    "private","protected","public","register","reinterpret_cast","return",
    "short","signed","sizeof","static","static_cast","struct","switch",
    "template","this","throw","true","try","typedef","typeid","typename",
    "union","unsigned","using","virtual","void","volatile","while"
}

class CPPLexer(BaseLexer):

    name = "cpp"
    file_extensions = ["cpp", "hpp", "cc", "cxx", "h"]

    STRING_RE   = re.compile(r'"(\\.|[^"])*"')
    CHAR_RE     = re.compile(r"'(\\.|[^'])'")
    IDENT_RE    = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    FUNC_CALL_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    PREPROCESSOR_RE = re.compile(r"#\s*[A-Za-z_][A-Za-z0-9_]*")

    MULTI_OPS = [
        "==","!=", ">=","<=", "++","--", "&&","||",
        "<<", ">>", "+=","-=","*=","/=","%=",
        "::", "->", "->*", ".*"
    ]

    def lex(self, text):

        tokens = []
        lines = text.split("\n")

        protected = []   # Protected spans: strings, chars, comments

        # -------------------------------------------------------
        # 1) Strings, Chars, Single-line // Comments, Multi-line /* */
        # -------------------------------------------------------
        in_block_comment = False

        for ln, line in enumerate(lines, start=1):

            i = 0
            L = len(line)

            # MULTI-LINE COMMENTS /* ... */
            while i < L:
                if not in_block_comment and line.startswith("/*", i):
                    in_block_comment = True
                    start = i
                    i += 2
                    continue

                if in_block_comment:
                    endpos = line.find("*/", i)
                    if endpos == -1:
                        # continue comment to end of line
                        tokens.append(("comment", f"{ln}.{start}", f"{ln}.{L}"))
                        protected.append((ln, start, L))
                        break
                    else:
                        # comment ends on this line
                        tokens.append(("comment", f"{ln}.{start}", f"{ln}.{endpos+2}"))
                        protected.append((ln, start, endpos+2))
                        in_block_comment = False
                        i = endpos + 2
                        continue

                i += 1

            # STRING LITERALS
            for m in self.STRING_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("string", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, e))

            # CHAR LITERALS
            for m in self.CHAR_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("string", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, e))

            # SINGLE-LINE // COMMENTS
            if "//" in line:
                i = line.index("//")
                tokens.append(("comment", f"{ln}.{i}", f"{ln}.{len(line)}"))
                protected.append((ln, i, len(line)))
                
            m = self.PREPROCESSOR_RE.match(line)
            if m:
                s, e = m.start(), m.end()
                tokens.append(("preprocessor", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, len(line)))

        # -------------------------------------------------------
        # Helper: check if protected
        # -------------------------------------------------------
        def is_protected(line_no, col):
            for pl, a, b in protected:
                if pl == line_no and a <= col < b:
                    return True
            return False

        # -------------------------------------------------------
        # 2) IDENTIFIER, KEYWORD, FUNCTION CALL, OPERATORS
        # -------------------------------------------------------
        for ln, line in enumerate(lines, start=1):

            # IDENTIFIERS + KEYWORDS
            for m in self.IDENT_RE.finditer(line):
                s, e = m.start(), m.end()
                if is_protected(ln, s):
                    continue

                word = m.group(0)

                if word in CPP_KEYWORDS:
                    tokens.append(("keyword", f"{ln}.{s}", f"{ln}.{e}"))
                else:
                    tokens.append(("ident", f"{ln}.{s}", f"{ln}.{e}"))

            # FUNCTION CALLS: name(
            for m in self.FUNC_CALL_RE.finditer(line):
                s, e = m.start(1), m.end(1)
                name = m.group(1)

                if is_protected(ln, s):
                    continue
                if name in CPP_KEYWORDS:
                    continue

                tokens.append(("function", f"{ln}.{s}", f"{ln}.{e}"))

            # MULTI-CHAR OPERATORS
            for op in self.MULTI_OPS:
                idx = line.find(op)
                while idx != -1:
                    if not is_protected(ln, idx):
                        tokens.append(("operator", f"{ln}.{idx}", f"{ln}.{idx+len(op)}"))
                    idx = line.find(op, idx + 1)

            # SINGLE CHARACTER OPERATORS
            for i, ch in enumerate(line):
                if ch in "{}[]()+-*/%=!<>:;,.&|^~?":
                    if not is_protected(ln, i):
                        tokens.append(("operator", f"{ln}.{i}", f"{ln}.{i+1}"))

        return tokens
