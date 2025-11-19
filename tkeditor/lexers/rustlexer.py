from tkeditor.Lexers.baselexer import BaseLexer
import re

RUST_KEYWORDS = {
    "as", "break", "const", "continue", "crate", "else", "enum", "extern",
    "false", "fn", "for", "if", "impl", "in", "let", "loop", "match", "mod",
    "move", "mut", "pub", "ref", "return", "self", "Self", "static", "struct",
    "super", "trait", "true", "type", "unsafe", "use", "where", "while",
    "async", "await", "dyn", "abstract", "final", "macro", "override",
    "virtual"
}

class RustLexer(BaseLexer):

    name = "rust"
    file_extensions = ["rs"]

    # string regexes
    STRING_RE = re.compile(r'"(\\.|[^"])*"')
    RAW_STRING_RE = re.compile(r'r#*"(?:.|\n)*?"#*')  # supports r#"..."#, r##"..."## etc
    IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    FUNC_CALL_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    TYPE_RE = re.compile(r"\b(struct|enum|trait|type)\s+([A-Za-z_][A-Za-z0-9_]*)")

    def lex(self, text):
        tokens = []
        lines = text.split("\n")
        protected = []  # (line, start, end)

        # -----------------------------------
        # 1) Strings + Comments
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
                idx_raw = line.find('r#', start_idx)

                next_events = [i for i in [idx_slash, idx_block, idx_quote, idx_raw] if i != -1]
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
                    m = re.match(r'"(\\.|[^"])*"', line[next_idx:])
                    if m:
                        s, e = next_idx, next_idx + m.end()
                        tokens.append(("string", f"{ln}.{s}", f"{ln}.{e}"))
                        protected.append((ln, s, e))
                        start_idx = e
                        continue
                    else:
                        break
                elif next_idx == idx_raw:
                    m = re.match(r'r#*"(?:.|\n)*?"#*', line[next_idx:])
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
        # 2) Keywords, identifiers, functions, types, operators
        # -----------------------------------
        for ln, line in enumerate(lines, start=1):

            # type names
            for m in self.TYPE_RE.finditer(line):
                s, e = m.start(2), m.end(2)
                if not is_protected(ln, s):
                    tokens.append(("class", f"{ln}.{s}", f"{ln}.{e}"))

            # identifiers / keywords
            for m in self.IDENT_RE.finditer(line):
                s, e = m.start(), m.end()
                if is_protected(ln, s):
                    continue
                word = m.group(0)
                if word in RUST_KEYWORDS:
                    tokens.append(("keyword", f"{ln}.{s}", f"{ln}.{e}"))
                else:
                    tokens.append(("ident", f"{ln}.{s}", f"{ln}.{e}"))

            # function calls
            for m in self.FUNC_CALL_RE.finditer(line):
                fname = m.group(1)
                s, e = m.start(1), m.end(1)
                if is_protected(ln, s) or fname in RUST_KEYWORDS:
                    continue
                tokens.append(("function", f"{ln}.{s}", f"{ln}.{e}"))

            # operators
            for i, ch in enumerate(line):
                if ch in "{}[]()+-*/%=!<>:;,.&|^~?":
                    if not is_protected(ln, i):
                        tokens.append(("operator", f"{ln}.{i}", f"{ln}.{i+1}"))

        return tokens
