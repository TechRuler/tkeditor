from tkeditor.Lexers.baselexer import BaseLexer
from tkeditor.Lexers.csslexer import CSSLexer
from tkeditor.Lexers.jslexer import JavaScriptLexer
import re

HTML_KEYWORDS = { "html","head","body","title","meta","link","script","style","div","span", ... }

class HTMLLexer(BaseLexer):
    name = "html"
    file_extensions = ["html","htm"]

    TAG_RE = re.compile(r"</?[A-Za-z0-9_\-]+")
    ATTR_RE = re.compile(r'\b([a-zA-Z\-:]+)\b(?=\=)')
    STRING_RE = re.compile(r'"[^"]*"|\'[^\']*\'')
    COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
    OPERATOR_CHARS = set("<>/=:")

    def lex(self, text):
        tokens = []
        lines = text.split("\n")
        protected_lines = {}  # line_no -> list of (start, end)

        # -------------------------------
        # 1) Comments + Strings
        # -------------------------------
        for ln, line in enumerate(lines, start=1):
            protected_lines.setdefault(ln, [])
            for m in self.COMMENT_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("comment", f"{ln}.{s}", f"{ln}.{e}"))
                protected_lines[ln].append((s, e))
            for m in self.STRING_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("string", f"{ln}.{s}", f"{ln}.{e}"))
                protected_lines[ln].append((s, e))

        # -------------------------------
        # Helper: fast protected check
        # -------------------------------
        def is_protected(line_no, col):
            for s, e in protected_lines.get(line_no, []):
                if s <= col < e:
                    return True
            return False

        # -------------------------------
        # 2) Parse line by line
        # -------------------------------
        ln = 0
        while ln < len(lines):
            line = lines[ln]
            # detect <script> or <style>
            match = re.search(r"<(script|style)(.*?)>", line, re.IGNORECASE)
            if match:
                tag = match.group(1).lower()
                start_tag_start = match.start()
                start_tag_end = match.end()

                # highlight opening tag
                tokens.append(("tag", f"{ln+1}.{start_tag_start}", f"{ln+1}.{start_tag_end}"))

                start_ln = ln
                # find closing tag
                end_ln = ln
                while end_ln < len(lines):
                    end_match = re.search(rf"</{tag}>", lines[end_ln], re.IGNORECASE)
                    if end_match:
                        closing_tag_start = end_match.start()
                        closing_tag_end = end_match.end()
                        break
                    end_ln += 1
                else:
                    closing_tag_start = closing_tag_end = 0

                # highlight closing tag
                tokens.append(("tag", f"{end_ln+1}.{closing_tag_start}", f"{end_ln+1}.{closing_tag_end}"))

                # inner content between tags
                inner = "\n".join(lines[start_ln+1:end_ln])
                if tag == "style":
                    nested_tokens = CSSLexer().lex(inner)
                else:
                    nested_tokens = JavaScriptLexer().lex(inner)

                # adjust line offsets for nested tokens...


                # adjust line offsets
                for tok_type, start, end in nested_tokens:
                    s_line, s_col = map(int, start.split("."))
                    e_line, e_col = map(int, end.split("."))
                    s_line += start_ln + 1
                    e_line += start_ln + 1
                    tokens.append((tok_type, f"{s_line}.{s_col}", f"{e_line}.{e_col}"))
                    # protect nested lines
                    for l in range(s_line, e_line+1):
                        protected_lines.setdefault(l, []).append((0, len(lines[l-1])))

                ln = end_ln  # skip processed block
            else:
                # normal tags, attrs, operators
                for m in self.TAG_RE.finditer(line):
                    s, e = m.start(), m.end()
                    if not is_protected(ln+1, s):
                        tokens.append(("tag", f"{ln+1}.{s}", f"{ln+1}.{e}"))
                for m in self.ATTR_RE.finditer(line):
                    s, e = m.start(1), m.end(1)
                    if not is_protected(ln+1, s):
                        tokens.append(("attribute", f"{ln+1}.{s}", f"{ln+1}.{e}"))
                for i, ch in enumerate(line):
                    if ch in self.OPERATOR_CHARS and not is_protected(ln+1, i):
                        tokens.append(("operator", f"{ln+1}.{i}", f"{ln+1}.{i+1}"))
            ln += 1

        return tokens
