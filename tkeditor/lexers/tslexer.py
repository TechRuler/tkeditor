from tkeditor.Lexers.baselexer import BaseLexer
import re

TYPESCRIPT_KEYWORDS = {
    "abstract","any","as","asserts","bigint","boolean","break","case","catch","class",
    "continue","const","constructor","declare","default","delete","do","else","enum",
    "export","extends","false","finally","for","from","function","get","if","implements",
    "import","in","infer","instanceof","interface","is","keyof","let","module","namespace",
    "never","new","null","number","object","package","private","protected","public","readonly",
    "require","return","set","static","string","super","switch","symbol","this","throw",
    "true","try","type","typeof","undefined","unique","unknown","var","void","while","with",
    "yield"
}

class TypeScriptLexer(BaseLexer):

    name = "typescript"
    file_extensions = ["ts", "tsx"]

    STRING_RE = re.compile(r'"(\\.|[^"])*"|\'(\\.|[^\'])*\'|`(\\.|[^`])*`')
    IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    FUNC_CALL_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    CLASS_RE = re.compile(r"\b(class|interface)\s+([A-Za-z_][A-Za-z0-9_]*)")

    def lex(self, text):
        tokens = []
        lines = text.split("\n")
        protected = []  # (line, start, end)

        # -------------------------------
        # 1) Strings and comments
        # -------------------------------
        in_block_comment = False
        for ln, line in enumerate(lines, start=1):
            start_idx = 0
            while start_idx < len(line):
                if in_block_comment:
                    end_idx = line.find("*/", start_idx)
                    if end_idx == -1:
                        tokens.append(("comment", f"{ln}.{start_idx}", f"{ln}.{len(line)}"))
                        protected.append((ln, start_idx, len(line)))
                        break
                    else:
                        tokens.append(("comment", f"{ln}.{start_idx}", f"{ln}.{end_idx+2}"))
                        protected.append((ln, start_idx, end_idx+2))
                        start_idx = end_idx + 2
                        in_block_comment = False
                        continue

                idx_slash = line.find("//", start_idx)
                idx_block = line.find("/*", start_idx)
                idx_quote = min([i for i in [line.find('"', start_idx), line.find("'", start_idx), line.find('`', start_idx)] if i != -1], default=-1)

                if idx_slash != -1 and (idx_slash <= idx_quote or idx_quote == -1) and (idx_slash <= idx_block or idx_block == -1):
                    tokens.append(("comment", f"{ln}.{idx_slash}", f"{ln}.{len(line)}"))
                    protected.append((ln, idx_slash, len(line)))
                    break
                elif idx_block != -1 and (idx_block <= idx_quote or idx_quote == -1):
                    end_idx = line.find("*/", idx_block + 2)
                    if end_idx == -1:
                        tokens.append(("comment", f"{ln}.{idx_block}", f"{ln}.{len(line)}"))
                        protected.append((ln, idx_block, len(line)))
                        in_block_comment = True
                        break
                    else:
                        tokens.append(("comment", f"{ln}.{idx_block}", f"{ln}.{end_idx+2}"))
                        protected.append((ln, idx_block, end_idx+2))
                        start_idx = end_idx + 2
                        continue
                elif idx_quote != -1:
                    m = self.STRING_RE.match(line[idx_quote:])
                    if m:
                        s, e = idx_quote, idx_quote + m.end()
                        tokens.append(("string", f"{ln}.{s}", f"{ln}.{e}"))
                        protected.append((ln, s, e))
                        start_idx = e
                        continue
                    else:
                        break
                else:
                    break

        # -------------------------------
        # helper
        # -------------------------------
        def is_protected(line_no, col):
            for pl, a, b in protected:
                if pl == line_no and a <= col < b:
                    return True
            return False

        # -------------------------------
        # 2) Keywords, identifiers, functions, classes
        # -------------------------------
        for ln, line in enumerate(lines, start=1):

            # class / interface names
            for m in self.CLASS_RE.finditer(line):
                s, e = m.start(2), m.end(2)
                if not is_protected(ln, s):
                    tokens.append(("class", f"{ln}.{s}", f"{ln}.{e}"))

            # identifiers / keywords
            for m in self.IDENT_RE.finditer(line):
                s, e = m.start(), m.end()
                if is_protected(ln, s):
                    continue
                word = m.group(0)
                if word in TYPESCRIPT_KEYWORDS:
                    tokens.append(("keyword", f"{ln}.{s}", f"{ln}.{e}"))
                else:
                    tokens.append(("ident", f"{ln}.{s}", f"{ln}.{e}"))

            # function calls
            for m in self.FUNC_CALL_RE.finditer(line):
                fname = m.group(1)
                s, e = m.start(1), m.end(1)
                if is_protected(ln, s) or fname in TYPESCRIPT_KEYWORDS:
                    continue
                tokens.append(("function", f"{ln}.{s}", f"{ln}.{e}"))

            # operators
            for i, ch in enumerate(line):
                if ch in "{}[]()+-*/%=!<>:;,.&|^~?":
                    if not is_protected(ln, i):
                        tokens.append(("operator", f"{ln}.{i}", f"{ln}.{i+1}"))

        return tokens
