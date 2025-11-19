from tkeditor.Lexers.baselexer import BaseLexer
import keyword
import tokenize, io

PYTHON_KEYWORDS = set(keyword.kwlist)


class PythonLexer(BaseLexer):

    name = "python"
    file_extensions = ["py"]

    def lex(self, text):

        tokens = []
        src = io.StringIO(text)

        prev_tok = None

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
                if ttype == tokenize.STRING:
                    tokens.append(("string", start, end))
                
                elif ttype == tokenize.COMMENT:
                    tokens.append(("comment", start, end))

                elif ttype == tokenize.NUMBER:
                    tokens.append(("number", start, end))

                elif tstr in PYTHON_KEYWORDS:
                    tokens.append(("keyword", start, end))

                elif ttype == tokenize.OP:
                    tokens.append(("operator", start, end))

                elif ttype == tokenize.NAME:
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
                    fname_start = f"{prev_tok.start[0]}.{prev_tok.start[1]}"
                    fname_end   = f"{prev_tok.end[0]}.{prev_tok.end[1]}"
                    tokens.append(("function", fname_start, fname_end))

                prev_tok = tok

        except tokenize.TokenError:
            pass

        return tokens
