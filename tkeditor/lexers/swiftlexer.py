from tkeditor.Lexers.baselexer import BaseLexer
import re

SWIFT_KEYWORDS = {
    "associatedtype","class","deinit","enum","extension","fileprivate","func",
    "import","init","inout","internal","let","open","operator","private","protocol",
    "public","rethrows","return","static","struct","subscript","typealias","var",
    "break","case","continue","default","defer","do","else","fallthrough","for",
    "guard","if","in","repeat","switch","where","while","as","Any","catch","false",
    "is","nil","super","self","Self","throw","throws","true","try","__COLUMN__",
    "__FILE__","__FUNCTION__","__LINE__"
}

class SwiftLexer(BaseLexer):

    name = "swift"
    file_extensions = ["swift"]

    STRING_RE = re.compile(r'"(\\.|[^"])*"')
    IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    FUNC_CALL_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    CLASS_RE = re.compile(r"\b(class|struct|enum|protocol)\s+([A-Za-z_][A-Za-z0-9_]*)")

    def lex(self, text):
        tokens = []
        lines = text.split("\n")
        protected = []  # (line, start, end)

        # -----------------------------------
        # 1) Strings + comments
        # -----------------------------------
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
                idx_quote = line.find('"', start_idx)

                next_events = [i for i in [idx_slash, idx_block, idx_quote] if i != -1]
                if not next_events:
                    break
                next_idx = min(next_events)

                if next_idx == idx_slash:
                    tokens.append(("comment", f"{ln}.{next_idx}", f"{ln}.{len(line)}"))
                    protected.append((ln, next_idx, len(line)))
                    break
                elif next_idx == idx_block:
                    end_idx = line.find("*/", next_idx+2)
                    if end_idx == -1:
                        tokens.append(("comment", f"{ln}.{next_idx}", f"{ln}.{len(line)}"))
                        protected.append((ln, next_idx, len(line)))
                        in_block_comment = True
                        break
                    else:
                        tokens.append(("comment", f"{ln}.{next_idx}", f"{ln}.{end_idx+2}"))
                        protected.append((ln, next_idx, end_idx+2))
                        start_idx = end_idx + 2
                        continue
                elif next_idx == idx_quote:
                    m = self.STRING_RE.match(line[next_idx:])
                    if m:
                        s, e = next_idx, next_idx + m.end()
                        tokens.append(("string", f"{ln}.{s}", f"{ln}.{e}"))
                        protected.append((ln, s, e))
                        start_idx = e
                        continue
                    else:
                        break
                else:
                    break

        # -----------------------------------
        # helper
        # -----------------------------------
        def is_protected(line_no, col):
            for pl, a, b in protected:
                if pl == line_no and a <= col < b:
                    return True
            return False

        # -----------------------------------
        # 2) Keywords, identifiers, functions, classes
        # -----------------------------------
        for ln, line in enumerate(lines, start=1):

            # class / struct / enum / protocol names
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
                if word in SWIFT_KEYWORDS:
                    tokens.append(("keyword", f"{ln}.{s}", f"{ln}.{e}"))
                else:
                    tokens.append(("ident", f"{ln}.{s}", f"{ln}.{e}"))

            # function calls
            for m in self.FUNC_CALL_RE.finditer(line):
                fname = m.group(1)
                s, e = m.start(1), m.end(1)
                if is_protected(ln, s) or fname in SWIFT_KEYWORDS:
                    continue
                tokens.append(("function", f"{ln}.{s}", f"{ln}.{e}"))

            # operators
            for i, ch in enumerate(line):
                if ch in "{}[]()+-*/%=!<>:;,.&|^~?":
                    if not is_protected(ln, i):
                        tokens.append(("operator", f"{ln}.{i}", f"{ln}.{i+1}"))

        return tokens
