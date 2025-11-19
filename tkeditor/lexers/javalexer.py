from tkeditor.Lexers.baselexer import BaseLexer
import re


JAVA_KEYWORDS = {
    "int","char","float","double","void","long","short","byte","boolean",
    "for","while","do","if","else","switch","case","return","break","continue",
    "class","interface","extends","implements","new","try","catch","finally",
    "throw","throws","public","private","protected","static","final","abstract",
    "import","package","instanceof","super","this","volatile","synchronized",
    "native","transient","enum","assert","default",
}

class JavaLexer(BaseLexer):

    name = "java"
    file_extensions = ["java"]

    STRING_RE = re.compile(r'"(\\.|[^"])*"')
    CHAR_RE = re.compile(r"'(\\.|[^'])'")
    IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    FUNC_CALL_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    NUMBER_RE = re.compile(r"\b(0x[0-9A-Fa-f]+|0b[01]+|\d+(\.\d+)?([eE][+-]?\d+)?)\b")
    ANNOTATION_RE = re.compile(r"@([A-Za-z_][A-Za-z0-9_]*)")

    BLOCK_COMMENT_START = "/*"
    BLOCK_COMMENT_END = "*/"

    def lex(self, text):

        tokens = []
        lines = text.split("\n")
        protected = []

        in_block_comment = False
        block_start_col = 0

        # ---------------------------------------------------------
        # 1. STRINGS, CHARS, COMMENTS (protected regions)
        # ---------------------------------------------------------
        for ln, line in enumerate(lines, start=1):

            # block comment scanning (super fast linear)
            i = 0
            while i < len(line):
                if not in_block_comment:
                    if line.startswith("/*", i):
                        in_block_comment = True
                        block_start_col = i
                        i += 2
                    else:
                        i += 1
                else:
                    if line.startswith("*/", i):
                        tokens.append(("comment",
                                       f"{ln}.{block_start_col}",
                                       f"{ln}.{i+2}"))
                        protected.append((ln, block_start_col, i+2))
                        in_block_comment = False
                        i += 2
                    else:
                        i += 1

            if in_block_comment:
                tokens.append(("comment", f"{ln}.{block_start_col}", f"{ln}.{len(line)}"))
                protected.append((ln, block_start_col, len(line)))

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

            # single-line //
            if "//" in line and not in_block_comment:
                i = line.index("//")
                tokens.append(("comment", f"{ln}.{i}", f"{ln}.{len(line)}"))
                protected.append((ln, i, len(line)))

        # helper
        def is_protected(line_no, col):
            for pl, a, b in protected:
                if pl == line_no and a <= col < b:
                    return True
            return False

        # ---------------------------------------------------------
        # 2. IDENTIFIERS, KEYWORDS, FUNCTIONS, NUMBERS, ANNOTATIONS
        # ---------------------------------------------------------
        for ln, line in enumerate(lines, start=1):

            # annotations
            for m in self.ANNOTATION_RE.finditer(line):
                s, e = m.start(), m.end()
                if not is_protected(ln, s):
                    tokens.append(("annotation", f"{ln}.{s}", f"{ln}.{e}"))

            # numbers
            for m in self.NUMBER_RE.finditer(line):
                s, e = m.start(), m.end()
                if not is_protected(ln, s):
                    tokens.append(("number", f"{ln}.{s}", f"{ln}.{e}"))

            # identifiers + keywords
            for m in self.IDENT_RE.finditer(line):
                s, e = m.start(), m.end()

                if is_protected(ln, s):
                    continue

                word = m.group(0)

                if word in JAVA_KEYWORDS:
                    tokens.append(("keyword", f"{ln}.{s}", f"{ln}.{e}"))
                else:
                    tokens.append(("ident", f"{ln}.{s}", f"{ln}.{e}"))

            # function calls
            for m in self.FUNC_CALL_RE.finditer(line):
                fname = m.group(1)
                s, e = m.start(1), m.end(1)

                if is_protected(ln, s):
                    continue

                if fname not in JAVA_KEYWORDS:
                    tokens.append(("function", f"{ln}.{s}", f"{ln}.{e}"))

            # class / interface / enum names
            if line.strip().startswith(("class ", "interface ", "enum ")):
                parts = line.strip().split()
                if len(parts) >= 2:
                    # find identifier location manually
                    name = parts[1]
                    idx = line.index(name)
                    tokens.append(("classname",
                                   f"{ln}.{idx}",
                                   f"{ln}.{idx+len(name)}"))

            # operators
            for i, ch in enumerate(line):
                if ch in "{}[]()+-*/%=!<>:;,.&|^~?":
                    if not is_protected(ln, i):
                        tokens.append(("operator", f"{ln}.{i}", f"{ln}.{i+1}"))

        return tokens
