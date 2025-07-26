import re 
from tkeditor.lexers.base_lexer import BaseLexer
import keyword
import builtins
class PythonLexer(BaseLexer):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor.text
        self.custom_styles:dict = {}
        
        self.tags = ["keyword","builtin","functionName","className","method",
                     "attribute","number","decorator","constant","string","fstring","comments"]


        

    def set_custom_styles(self, custom_styles:dict):
        self.custom_styles = custom_styles
    
    def setup_tags(self):
        default_tags = {
            "keyword": {"foreground": "#FF9D00"},
            "attribute": {"foreground": "#61AFEF"},
            "method": {"foreground": "#C678DD"},
            "functionName": {"foreground": "#C678DD"},
            "className": {"foreground": "#C678DD"},
            "builtin": {"foreground": "#F122DA"},
            "constant":{"foreground": "#98C379"},
            "comments": {"foreground": "#5C6370"},
            "string": {"foreground": "#98C379"},
            "fstring": {"foreground": "#864379"},
        }

        for tag, default_config in default_tags.items():
            merged_config = default_config.copy()
            if tag in self.custom_styles:
                merged_config.update(self.custom_styles[tag])
            self.editor.tag_configure(tag, **merged_config)
    
    def highlight(self):
        # Get the visible code range
        for tag in self.tags:
            self.editor.tag_remove(tag, '1.0', 'end')
        
        first_index = self.editor.index("@0,0")
        first = self.editor.index(f"{first_index} -4line")
        last = self.editor.index(f"@0,{self.editor.winfo_height()} +4line")
        code = self.editor.get(first, last)

        self._attributes(code, first)
        self._keywords_builtin_methods_class_etc(code, first)
        self._string(self.editor.get('1.0','end'), self.editor.index('1.0'))
        self._fstrings(self.editor.get('1.0','end'), self.editor.index('1.0'))
        self._comment(code, first)


        
    def _string(self, code: str, first: str):
        
        lines = code.split('\n')
        line_offsets = []
        offset = 0
        for line in lines:
            line_offsets.append(offset)
            offset += len(line) + 1  # +1 for \n

        def is_in_comment(pos: int) -> bool:
            line_num = code[:pos].count('\n')
            line = lines[line_num]
            line_offset = line_offsets[line_num]
            hash_index = line.find("#")
            return 0 <= hash_index < (pos - line_offset)

        string_spans = []

        # 1. Highlight real triple-quoted strings (multiline allowed)
        triple_pattern = r"('''.*?'''|\"\"\".*?\"\"\")"
        for match in re.finditer(triple_pattern, code, re.DOTALL):
            start, end = match.span()
            if is_in_comment(start):
                continue
            # Skip if this triple quote is inside a single/double-quoted string like `"'''"`
            prefix_area = code[max(0, start - 3):start]
            if '"' in prefix_area or "'" in prefix_area:
                continue
            string_spans.append((start, end))
            self.editor.tag_add("string", f"{first} + {start}c", f"{first} + {end}c")

        # 2. Highlight single-line quoted strings (not triple-quoted)
        single_pattern = r'(?<!["\'])("([^"\\\n]|\\.)*?"|\'([^\'\\\n]|\\.)*?\')'
        for match in re.finditer(single_pattern, code):
            start, end = match.span()
            if is_in_comment(start):
                continue
            # Skip if inside triple-quoted strings
            if any(s <= start < e for s, e in string_spans):
                continue
            string_spans.append((start, end))
            self.editor.tag_add("string", f"{first} + {start}c", f"{first} + {end}c")

        # 3. Highlight unterminated strings on single line (but skip lines with triple quotes)
        offset = 0
        for line in lines:
            if "'''" in line or '"""' in line:
                offset += len(line) + 1
                continue
            for qt in ("'", '"'):
                if line.count(qt) % 2 == 1:
                    quote_index = line.find(qt)
                    abs_start = offset + quote_index
                    if not is_in_comment(abs_start) and not any(s <= abs_start < e for s, e in string_spans):
                        self.editor.tag_add("string",
                                            f"{first} + {abs_start}c",
                                            f"{first} + {offset + len(line)}c")
            offset += len(line) + 1



    def _fstrings(self, code: str, first: str):
        lines = code.split('\n')
        line_offsets = []
        offset = 0
        for line in lines:
            line_offsets.append(offset)
            offset += len(line) + 1

        def is_in_comment(pos: int) -> bool:
            line_num = code[:pos].count('\n')
            line = lines[line_num]
            line_offset = line_offsets[line_num]
            hash_index = line.find("#")
            return 0 <= hash_index < (pos - line_offset)

        def tag_range(tag: str, start: int, end: int):
            self.editor.tag_add(tag, f"{first} + {start}c", f"{first} + {end}c")

        # Match f-strings (both single-line and triple-quoted)
        fstring_pattern = r'''(?ix)       # ignore case, allow comments
            (?<![a-zA-Z0-9_])             # not part of identifier
            (f|rf|fr)                     # f-string prefix
            (                             # group 2: quote block
            (''' + r"'''(?:\\.|[^\\])*?'''" + r''')   # triple-single
            | ("""(?:\\.|[^\\])*?""")     # triple-double
            | ('(?:\\.|[^\\'\n])*?')      # single
            | ("(?:\\.|[^\\\"\n])*?")     # double
            )
        '''

        for match in re.finditer(fstring_pattern, code, re.DOTALL):
            start, end = match.span()
            if is_in_comment(start):
                continue
            tag_range("fstring", start, end)
    def _comment(self, code, first):
        # Step 1: collect spans of strings (so we can ignore them)
        string_pattern = r"'''(?:\\.|[^\\])*?'''|\"\"\"(?:\\.|[^\\])*?\"\"\"|\"(?:\\.|[^\\\"\n])*?\"|'(?:\\.|[^\\'\n])*?'"
        string_spans = []
        for match in re.finditer(string_pattern, code, re.DOTALL):
            string_spans.append(match.span())

        def is_inside_string(index):
            for start, end in string_spans:
                if start <= index < end:
                    return True
            return False

        # Step 2: highlight real comments (not inside strings)
        for match in re.finditer(r'#.*', code):
            start, end = match.span()
            if not is_inside_string(start):
                self.editor.tag_add("comments", f"{first} + {start}c", f"{first} + {end}c +1c")
    def _keywords_builtin_methods_class_etc(self, code, first):
        snytax: dict = {
            "keyword": r"\b(" + "|".join(keyword.kwlist) + r")\b",
            "builtin": r"\b(" + "|".join(re.escape(name) for name in dir(builtins)) + r")\b",
            # "attribute": r"(?<!\bfrom\s)(?<!\bimport\s)\.(\w+)",
            "functionName": r"\bdef\s+([a-zA-Z_]\w*)",
            "className": r"\bclass\s+([a-zA-Z_]\w*)",
            "method": r"\b([a-zA-Z_]\w*)\s*(?=\()",  # general function calls
            "number": r"\b\d+(\.\d+)?\b",
            "decorator": r"@(\w+)",
            "constant": r"\b(True|False|None)\b"
        }
        for tag, pattern in snytax.items():
            self._highlight(pattern, tag, code, first)
    def _attributes(self, code, first):
        attribute_pattern = r"\.(\w+)"
        for match in re.finditer(attribute_pattern, code):
            start, end = match.span(1)
            
            # Get line where match occurs
            line_no = code[:start].count("\n")
            line_start = code.rfind("\n", 0, start) + 1
            line = code[line_start:code.find("\n", start) if "\n" in code[start:] else len(code)]

            # Don't highlight if inside an import or from statement
            if re.match(r'^\s*(from|import)\s', line.strip()):
                continue

            self.editor.tag_add("attribute", f"{first} + {start}c", f"{first} + {end}c")

    def _highlight(self, pattern, tag, code, first):
        for match in re.finditer(pattern, code):
            if match.lastindex:
                start_idx = match.start(1)
                end_idx = match.end(1)
            else:
                start_idx = match.start()
                end_idx = match.end()
            start = self.editor.index(f"{first} + {start_idx}c")
            end = self.editor.index(f"{first} + {end_idx}c")
            self.editor.tag_add(tag, start, end)