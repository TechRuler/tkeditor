class BaseLexer:
    """Base class for all lexers."""

    name = "base"
    file_extensions = []   # ["py"], ["js"], etc.

    # tag colors (editor will configure tag based on this)
    styles = {
        "keyword":  "#ff006e",
        "string":   "#00a896",
        "comment":  "#6c757d",
        "number":   "#f72585",
        "operator": "#f4a261",
        "ident":    "#ffffff",
        "function": "#4dd0e1",
        "class":    "#4dd0e1"
    }

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
