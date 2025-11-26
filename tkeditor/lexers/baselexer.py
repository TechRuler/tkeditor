class BaseLexer:
    """Base class for all lexers."""
    name = "base"
    file_extensions = []   # ["py"], ["js"], etc.
    def __init__(self):

        
        self.default_styles = {
            # ---------- Core ----------
            "ident":        {"foreground":"#000000"},  # default text / variables
            "keyword":      {"foreground":"#ff4791"},  # bright pink / for keywords like if, else, return
            "function":     {"foreground":"#4d79ff"},  # function names
            "class":        {"foreground":"#ad6cff"},  # class names
            "operator":     {"foreground":"#ff8c42"},  # + - * / = etc
            "number":       {"foreground":"#f9c74f"},  # numeric literals
            "string":       {"foreground":"#00ff9c"},  # string literals
            "f_expr":       {"foreground":"#00ff9c"},  # string literals
            "comment":      {"foreground":"#9ca0a6"},  # comments, gray
            "decorator":    {"foreground":"#de5602"},
            # ---------- HTML / XML ----------
            "tag":          {"foreground":"#ff6e6e"},  # <html>, <div> etc
            "attribute":    {"foreground":"#f4a261"},  # class, id, src
            "value":        {"foreground":"#00ff9c"},  # attribute values (strings)
            
            # ---------- CSS ----------
            "property":     {"foreground":"#ffb347"},  # color, width, font-size
            "selector":     {"foreground":"#ad6cff"},  # .class, #id, tag selectors
            "unit":         {"foreground":"#f72585"},  # px, em, %
            
            # ---------- C / C++ ----------
            "preprocessor": {"foreground":"#ff6f61"},  # #include, #define
            
        }
    
    def set_styles(self, styles:dict):
        self.styles = styles

    def get_styles(self):
        if hasattr(self, "styles"):
            return self.styles
        else:
            return self.default_styles


    def lex(self, text):
        """
        MUST return list of tuples:
        [
            ("token_type", "start_index", "end_index"),
            ...
        ]
        Example: ("keyword", "1.0", "1.3")
        """
        raise NotImplementedError
