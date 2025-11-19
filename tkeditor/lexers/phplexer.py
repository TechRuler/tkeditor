from tkeditor.Lexers.baselexer import BaseLexer
import re

PHP_KEYWORDS = {
    "abstract","and","array","as","break","callable","case","catch","class",
    "clone","const","continue","declare","default","do","else","elseif","enddeclare",
    "endfor","endforeach","endif","endswitch","endwhile","extends","final","finally",
    "for","foreach","function","global","goto","if","implements","include","include_once",
    "instanceof","insteadof","interface","isset","list","namespace","new","or","print",
    "private","protected","public","require","require_once","return","static","switch",
    "throw","trait","try","unset","use","var","while","xor","yield","true","false","null"
}

class PHPLexer(BaseLexer):

    name = "php"
    file_extensions = ["php"]

    # regex
    STRING_RE = re.compile(r'"(\\.|[^"])*"|\'(\\.|[^\'])*\'')
    IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    FUNC_CALL_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    CLASS_RE = re.compile(r"\b(class|interface|trait)\s+([A-Za-z_][A-Za-z0-9_]*)")

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

                # single line comments
                idx_slash = line.find("//", start_idx)
                idx_hash = line.find("#", start_idx)
                idx_block = line.find("/*", start_idx)
                idx_quote = line.find('"', start_idx)
                idx_single_quote = line.find("'", start_idx)

                next_events = [i for i in [idx_slash, idx_hash, idx_block, idx_quote, idx_single_quote] if i != -1]
                if not next_events:
                    break
                next_idx = min(next_events)

                if next_idx == idx_slash or next_idx == idx_hash:
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
                elif next_idx == idx_quote or next_idx == idx_single_quote:
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

            # class/interface/trait names
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
                if word in PHP_KEYWORDS:
                    tokens.append(("keyword", f"{ln}.{s}", f"{ln}.{e}"))
                else:
                    tokens.append(("ident", f"{ln}.{s}", f"{ln}.{e}"))

            # function calls
            for m in self.FUNC_CALL_RE.finditer(line):
                fname = m.group(1)
                s, e = m.start(1), m.end(1)
                if is_protected(ln, s) or fname in PHP_KEYWORDS:
                    continue
                tokens.append(("function", f"{ln}.{s}", f"{ln}.{e}"))

            # operators
            for i, ch in enumerate(line):
                if ch in "{}[]()+-*/%=!<>:;,.&|^~?":
                    if not is_protected(ln, i):
                        tokens.append(("operator", f"{ln}.{i}", f"{ln}.{i+1}"))

        return tokens
