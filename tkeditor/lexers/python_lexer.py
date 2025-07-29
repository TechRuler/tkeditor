import re 
from tkeditor.lexers.base_lexer import BaseLexer
import keyword
import builtins
class PythonLexer(BaseLexer):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor.text
        self.custom_styles:dict = {}
        
        self.__tags = ["keyword","builtin","functionName","className","method","string_prefix",
                       "attribute","number","decorator","constant","string","comments","bracketsopen","bracketsclose","words"]
        

        self.words = {}
    def style_key(self):
        tag = self.__tags
        tag.remove("words")
        tag.remove("bracketsopen")
        tag.remove("bracketsclose")
        tag.append("bracket")
        return tag
    
    def add_word_to_highlight(self, word:str, color:str):
        self.words[word] = color
        self.editor.tag_configure(word, **color)

    def set_custom_styles(self, custom_styles:dict):
        self.custom_styles = custom_styles

    def setup_tags(self):
        common_style = {
            "underline": False,
            "background": self.editor.cget('bg'),
            "font": self.editor.cget('font')
        }
        default_tags = {
            "string_prefix": {"foreground": "#FF9D00",**common_style},
            "attribute": {"foreground": "#61AFEF",**common_style},
            "method": {"foreground": "#C678DD",**common_style},
            "functionName": {"foreground": "#C678DD",**common_style},
            "decorator":{"foreground": "#FF9D00",**common_style},
            "builtin": {"foreground": "#F122DA",**common_style},
            "className": {"foreground": "#C678DD",**common_style},
            "bracket": {"foreground": "#61AFEF",**common_style},
            "number":{"foreground": "#98C379",**common_style},
            "operator":{"foreground": "#98C379",**common_style},
            "keyword": {"foreground": "#FF9D00",**common_style},
            "constant":{"foreground": "#98C379",**common_style},
            "comments": {"foreground": "#5C6370",**common_style},
            "string": {"foreground": "#98C379",**common_style},
        }

        for tag, default_config in default_tags.items():
            if tag == 'bracket':
                merged_config = default_config.copy()
                if tag in self.custom_styles:
                    merged_config.update(self.custom_styles[tag])
                self.editor.tag_configure("bracketsopen", **merged_config)
                self.editor.tag_configure("bracketsclose", **merged_config)
            else:
                merged_config = default_config.copy()
                if tag in self.custom_styles:
                    merged_config.update(self.custom_styles[tag])
                self.editor.tag_configure(tag, **merged_config)
        self.editor.tag_raise('sel')
        color = self.editor.cget('selectbackground') if self.editor.cget('selectbackground') else "#264F78"
        self.editor.tag_configure("sel", background=color, foreground="") 
    
    def highlight(self):
        # Get the visible code range
        for tag in self.__tags:
            self.editor.tag_remove(tag, '1.0', 'end')
        
        first_index = self.editor.index("@0,0")
        first = self.editor.index(f"{first_index} -4line")
        last = self.editor.index(f"@0,{self.editor.winfo_height()} +4line")
        code = self.editor.get(first, last)
        for word in self.words:
            self._highlight(fr'\b{word}\b',word, code, first)
        self._attributes(code, first)
        self._keywords_builtin_methods_class_etc(code, first)
        self._string(self.editor.get('1.0','end'), self.editor.index('1.0'))
        self._comment(code, first)
    def _string(self, code: str, first: str):
        # Step 1: Define all string regexes
        stringprefix = r"(?i:r|u|f|fr|rf|b|br|rb)?"
        sq3 = stringprefix + r"'''(?:[^\\]|\\.|\\\n)*?(?:'''|$)"
        dq3 = stringprefix + r'"""(?:[^\\]|\\.|\\\n)*?(?:"""|$)'
        sq = stringprefix + r"'(?:[^'\\\n]|\\.)*'?"
        dq = stringprefix + r'"(?:[^"\\\n]|\\.)*"?'
        string_pattern = f"{sq3}|{dq3}|{sq}|{dq}"

        string_spans = []
        for match in re.finditer(string_pattern, code, re.DOTALL):
            start, end = match.span()
            string_spans.append((start, end))

        def is_in_string(pos):
            for s_start, s_end in string_spans:
                if s_start <= pos < s_end:
                    return True
            return False

        # Step 2: Detect only real comments (outside of strings)
        comment_spans = []
        for match in re.finditer(r"#.*", code):
            start = match.start()
            if not is_in_string(start):
                comment_spans.append(match.span())

        def is_in_comment(start, end):
            for c_start, c_end in comment_spans:
                if start >= c_start and end <= c_end:
                    return True
            return False

        # Step 3: Highlight all strings
        for start, end in string_spans:
            text = code[start:end]
            if is_in_comment(start, end):
                continue

            prefix_match = re.match(r"(?i)(f|fr|rf)", text)
            if prefix_match:
                string_body = text[prefix_match.end():]
                base_pos = start + prefix_match.end()
                pos = 0
                depth = 0
                part_start = 0
                while pos < len(string_body):
                    if string_body[pos] == '{':
                        if depth == 0 and pos > part_start:
                            s = base_pos + part_start
                            e = base_pos + pos
                            if not is_in_comment(s, e):
                                self.editor.tag_add("string", f"{first} + {s}c", f"{first} + {e}c")
                        depth += 1
                        part_start = pos + 1
                    elif string_body[pos] == '}':
                        depth -= 1
                        if depth == 0:
                            part_start = pos + 1
                    pos += 1
                if part_start < len(string_body) and depth == 0:
                    s = base_pos + part_start
                    e = base_pos + len(string_body)
                    if not is_in_comment(s, e):
                        self.editor.tag_add("string", f"{first} + {s}c", f"{first} + {e}c")
            else:
                self.editor.tag_add("string", f"{first} + {start}c", f"{first} + {end}c")


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
        all_builtins = dir(builtins)

        # Remove __dunder__ names and keywords
        filtered_builtins = [
            name for name in all_builtins
            if not (name.startswith("__") and name.endswith("__")) and name not in keyword.kwlist
        ]
        keywords = list(keyword.kwlist)
        keywords.remove('True')
        keywords.remove('False')
        keywords.remove('None')
        keywords.append('self')
        snytax: dict = {
            "keyword": r"\b(" + "|".join(keywords) + r")\b",
            "string_prefix":r"(?i)\b(r|u|f|fr|rf|b|br|rb)(?=['\"])",
            "method": r"\b([a-zA-Z_]\w*)\s*(?=\()",  # general function calls
            "functionName": r"\bdef\s+([a-zA-Z_]\w*)",
            "className": r"\bclass\s+([a-zA-Z_]\w*)",
            "builtin": r"\b(" + "|".join(re.escape(name) for name in filtered_builtins) + r")\b",
            "bracketsopen": r"[\(\[\{]",
            "bracketsclose":r"[\)\]\}]",
            "operator":r"[\*\+\-\/=<>]",
            "number": r"\b\d+(\.\d+)?\b",
            "decorator": r"@\w+",
            "constant": r"\b(True|False|None|[A-Z_]{2,})\b"
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