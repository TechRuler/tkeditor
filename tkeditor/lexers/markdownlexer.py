from tkeditor.Lexers.baselexer import BaseLexer
import re

class MarkdownLexer(BaseLexer):
    name = "markdown"
    file_extensions = ["md", "markdown"]

    # Patterns
    HEADER_RE = re.compile(r'^(#{1,6})\s+(.*)')
    BOLD_RE = re.compile(r'\*\*(.*?)\*\*|__(.*?)__')
    ITALIC_RE = re.compile(r'\*(.*?)\*|_(.*?)_')
    INLINE_CODE_RE = re.compile(r'`([^`]*)`')
    CODE_BLOCK_RE = re.compile(r'```.*?```', re.DOTALL)
    LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    LIST_RE = re.compile(r'^\s*([-*+]|[0-9]+\.)\s+')
    HTML_COMMENT_RE = re.compile(r'<!--(.*?)-->')

    def lex(self, text):
        tokens = []
        lines = text.split("\n")
        protected = []  # (line, start, end)

        # 1) Comments (protected)
        for ln, line in enumerate(lines, start=1):
            for m in self.HTML_COMMENT_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("comment", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, e))

        def is_protected(line_no, col):
            for pl, s, e in protected:
                if pl == line_no and s <= col < e:
                    return True
            return False

        # 2) Process each line
        for ln, line in enumerate(lines, start=1):

            # Headers
            m = self.HEADER_RE.match(line)
            if m:
                s, e = m.start(2), m.end(2)
                tokens.append(("keyword", f"{ln}.{s}", f"{ln}.{e}"))

            # Lists
            for m in self.LIST_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("operator", f"{ln}.{s}", f"{ln}.{e}"))

            # Inline code
            for m in self.INLINE_CODE_RE.finditer(line):
                s, e = m.start(), m.end()
                tokens.append(("string", f"{ln}.{s}", f"{ln}.{e}"))
                protected.append((ln, s, e))

            # Bold
            for m in self.BOLD_RE.finditer(line):
                s, e = m.start(), m.end()
                if not is_protected(ln, s):
                    tokens.append(("keyword", f"{ln}.{s}", f"{ln}.{e}"))

            # Italic
            for m in self.ITALIC_RE.finditer(line):
                s, e = m.start(), m.end()
                if not is_protected(ln, s):
                    tokens.append(("ident", f"{ln}.{s}", f"{ln}.{e}"))

            # Links
            for m in self.LINK_RE.finditer(line):
                s, e = m.start(1), m.end(1)
                tokens.append(("function", f"{ln}.{s}", f"{ln}.{e}"))  # link text
                s2, e2 = m.start(2), m.end(2)
                tokens.append(("string", f"{ln}.{s2}", f"{ln}.{e2}"))  # link URL

        # Code blocks (multiline)
        for m in self.CODE_BLOCK_RE.finditer(text):
            start_line = text[:m.start()].count("\n") + 1
            end_line = text[:m.end()].count("\n") + 1
            tokens.append(("string", f"{start_line}.0", f"{end_line}.0"))

        return tokens
