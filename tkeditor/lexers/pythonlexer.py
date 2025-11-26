from tkeditor.Lexers.baselexer import BaseLexer
import keyword
import tokenize, io

PYTHON_KEYWORDS = set(keyword.kwlist + [
    "self", "cls"])


class PythonLexer(BaseLexer):

    name = "python"
    file_extensions = ["py"]
    def __init__(self):
        super().__init__()
        self.identifiers = set()
    def lex(self, text):

        tokens = []
        src = io.StringIO(text)

        prev_tok = None
        prev_tok_is_decorator = False  # initialize here!
        in_fstring = False
        store_word = []
        

        try:
            for tok in tokenize.generate_tokens(src.readline):

                ttype = tok.type
                tstr  = tok.string

                sline, scol = tok.start
                eline, ecol = tok.end

                start = f"{sline}.{scol}"
                end   = f"{eline}.{ecol}"

                # ====================================================
                # 1) BASIC TOKENS
                # ====================================================
                # -------------------------------
                # f-string handling
                # -------------------------------
                if ttype == tokenize.FSTRING_START:
                    tokens.append(("string", start, end))
                    in_fstring = True

                elif ttype == tokenize.FSTRING_MIDDLE:
                    # The literal parts between {…} are string
                    # Expressions inside {} are separate tokens
                    if "{" in tstr or "}" in tstr:
                        tokens.append(("f_expr", start, end))
                    else:
                        tokens.append(("string", start, end))

                elif ttype == tokenize.FSTRING_END:
                    tokens.append(("string", start, end))
                    in_fstring = False
                    
                if ttype == tokenize.STRING:
                    tokens.append(("string", start, end))
                elif ttype == tokenize.COMMENT:
                    tokens.append(("comment", start, end))

                elif ttype == tokenize.NUMBER:
                    tokens.append(("number", start, end))

                elif tstr in PYTHON_KEYWORDS:
                    tokens.append(("keyword", start, end))

                elif ttype == tokenize.OP:
                    if tstr == "@":
                        prev_tok_is_decorator = True
                        tokens.append(("operator", start, end))
                    else:
                        tokens.append(("operator", start, end))

                elif ttype == tokenize.NAME:
                    
                    if prev_tok_is_decorator:
                        tokens.append(("decorator", f"{sline}.{scol}", f"{eline}.{ecol}"))
                        prev_tok_is_decorator = False
                    else:
                        tokens.append(("ident", start, end))
                        
                        
                        

                
                # ====================================================
                # 2) CLASS NAME DETECTION: class NAME
                # ====================================================
                if (
                    prev_tok and
                    prev_tok.string == "class" and
                    ttype == tokenize.NAME
                ):
                    tokens.append(("class", start, end))


                # ====================================================
                # 3) FUNCTION CALL DETECTION: name (
                #    FIXED: do NOT mark keywords as functions
                #    FIXED: do NOT mark inside strings/comments
                # ====================================================
                if (
                    prev_tok and
                    prev_tok.type == tokenize.NAME and
                    prev_tok.string not in PYTHON_KEYWORDS and  # IMPORTANT FIX
                    ttype == tokenize.OP and
                    tstr == "("
                ):
                    # mark prev token as function
                    # fname_start = f"{prev_tok.start[0]}.{prev_tok.start[1]}"
                    # fname_end   = f"{prev_tok.end[0]}.{prev_tok.end[1]}"
                    # tokens.append(("function", fname_start, fname_end))
                    # skip if prev_tok is decorator (@name)
                    if prev_tok.start[0] == tok.start[0]:  # same line as '('
                        tokens.append(("function", f"{prev_tok.start[0]}.{prev_tok.start[1]}", f"{prev_tok.end[0]}.{prev_tok.end[1]}"))

                prev_tok = tok

        except tokenize.TokenError:
            pass

        return tokens

