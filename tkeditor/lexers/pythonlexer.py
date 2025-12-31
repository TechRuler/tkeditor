from tkeditor.lexers.baselexer import BaseLexer
import keyword
import tokenize
import io
import builtins
import types

PYTHON_KEYWORDS = {*keyword.kwlist, "self", "cls"}

BUILTIN_VALUES = {
    name for name in dir(builtins)
    if not name.startswith('__')                        # remove dunder
    and (
        not callable(getattr(builtins, name))           # constants
        or isinstance(getattr(builtins, name), type)    # types/classes
        or isinstance(getattr(builtins, name), types.ModuleType) # modules
    )
}


class PythonLexer(BaseLexer):
    name = "python"
    file_extensions = ["py"]

    def __init__(self):
        super().__init__()

    def lex(self, text):
        tokens = []
        readline = io.StringIO(text).readline

        prev_tok = None
        prev_is_decorator = False

        try:
            for tok in tokenize.generate_tokens(readline):
                ttype = tok.type
                tstr = tok.string

                # ------------------------------------------------
                # STRINGS / COMMENTS / NUMBERS
                # ------------------------------------------------
                if ttype in (tokenize.STRING,
                             tokenize.FSTRING_START,
                             tokenize.FSTRING_MIDDLE,
                             tokenize.FSTRING_END):
                    tokens.append(("string",
                                   f"{tok.start[0]}.{tok.start[1]}",
                                   f"{tok.end[0]}.{tok.end[1]}"))

                elif ttype == tokenize.COMMENT:
                    tokens.append(("comment",
                                   f"{tok.start[0]}.{tok.start[1]}",
                                   f"{tok.end[0]}.{tok.end[1]}"))

                elif ttype == tokenize.NUMBER:
                    tokens.append(("number",
                                   f"{tok.start[0]}.{tok.start[1]}",
                                   f"{tok.end[0]}.{tok.end[1]}"))

                # ------------------------------------------------
                # KEYWORDS
                # ------------------------------------------------
                elif tstr in PYTHON_KEYWORDS:
                    tokens.append(("keyword",
                                   f"{tok.start[0]}.{tok.start[1]}",
                                   f"{tok.end[0]}.{tok.end[1]}"))
                
                elif tstr in BUILTIN_VALUES:
                    tokens.append(("builtin",
                                   f"{tok.start[0]}.{tok.start[1]}",
                                   f"{tok.end[0]}.{tok.end[1]}"))

                # ------------------------------------------------
                # OPERATORS
                # ------------------------------------------------
                elif ttype == tokenize.OP:
                    if tstr == "@":
                        prev_is_decorator = True

                    tokens.append(("operator",
                                   f"{tok.start[0]}.{tok.start[1]}",
                                   f"{tok.end[0]}.{tok.end[1]}"))

                    # function call detection: name (
                    if (prev_tok and
                        prev_tok.type == tokenize.NAME and
                        prev_tok.string not in PYTHON_KEYWORDS and
                        tstr == "(" and
                        prev_tok.start[0] == tok.start[0]):

                        tokens.append(("function",
                                       f"{prev_tok.start[0]}.{prev_tok.start[1]}",
                                       f"{prev_tok.end[0]}.{prev_tok.end[1]}"))

                # ------------------------------------------------
                # IDENTIFIERS
                # ------------------------------------------------
                elif ttype == tokenize.NAME:
                    if prev_is_decorator:
                        tokens.append(("decorator",
                                       f"{tok.start[0]}.{tok.start[1]}",
                                       f"{tok.end[0]}.{tok.end[1]}"))
                        prev_is_decorator = False
                    else:
                        tokens.append(("ident",
                                       f"{tok.start[0]}.{tok.start[1]}",
                                       f"{tok.end[0]}.{tok.end[1]}"))

                    # class NAME
                    if prev_tok and prev_tok.string == "class":
                        tokens.append(("class",
                                       f"{tok.start[0]}.{tok.start[1]}",
                                       f"{tok.end[0]}.{tok.end[1]}"))

                prev_tok = tok

        except tokenize.TokenError:
            pass

        return tokens
