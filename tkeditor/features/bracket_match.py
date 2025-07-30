import tokenize
import io
class BracketTracker:
    def __init__(self, text_widget, color=None):
        self.text_widget = text_widget
        bgcolor = color if color else 'lightblue'
        self.text_widget.tag_configure("BracketTracker", background = bgcolor)
        self.text_widget.bind("<KeyRelease>", lambda e:self.track_brackets(), add="+")
        self.text_widget.bind("<Button-1>", lambda e: self.text_widget.after_idle(self.track_brackets), add="+")
    def set_color(self, color):
        """Set the color for bracket tracking."""
        self.text_widget.tag_configure("BracketTracker", background = color)
    def track_brackets(self):
        self.text_widget.tag_remove("BracketTracker", "1.0", "end")

        cursor_index = self.text_widget.index("insert")
        line = self.text_widget.get("insert linestart", "insert lineend")
        col = int(cursor_index.split(".")[1])

        # Do not stop here — we only skip brackets *inside* strings/comments
        pre_word = self.text_widget.get("insert -1c", "insert")
        after_word = self.text_widget.get("insert", "insert +1c")

        try:
            if pre_word == ")":
                self._match_backwards(")")
            elif after_word == "(":
                self._match_forwards("(")
            else:
                # Handle case where cursor is BETWEEN matching ()
                # like:   (|)  ← cursor is between
                prev = self.text_widget.get("insert -1c", "insert")
                next = self.text_widget.get("insert", "insert +1c")
                if prev == "(" and next == ")":
                    # Check that neither bracket is inside string/comment
                    line = self.text_widget.get("insert linestart", "insert lineend")
                    col = int(self.text_widget.index("insert").split(".")[1])
                    if not self.is_inside_string_or_comment(line, col - 1) and not self.is_inside_string_or_comment(line, col):
                        self.text_widget.tag_add("BracketTracker", "insert -1c", "insert")
                        self.text_widget.tag_add("BracketTracker", "insert", "insert +1c")
                else:
                    # Try find surrounding bracket
                    open_index = self._match_backwards(")", return_only=True)
                    if open_index:
                        self.text_widget.mark_set("match_temp", open_index)
                        close_index = self._match_forwards("(", return_only=True, start_index="match_temp +1c")
                        if close_index:
                            self.text_widget.tag_add("BracketTracker", open_index, f"{open_index} +1c")
                            self.text_widget.tag_add("BracketTracker", close_index, f"{close_index} +1c")
        except Exception as e:
            print("Bracket track error:", e)

    def _match_backwards(self, close_char, return_only=False, start_index=None):
        b = 1
        current_index = start_index or self.text_widget.index("insert -1c")

        while True:
            if current_index == "1.0":
                break  

            current_index = self.text_widget.index(f"{current_index} -1c")
            word = self.text_widget.get(current_index, f"{current_index} +1c")
            if word == close_char:
                b += 1
            elif word == "(":
                b -= 1
            if b == 0:
                if return_only:
                    return current_index
                self.text_widget.tag_add("BracketTracker", current_index, f"{current_index} +1c")
                self.text_widget.tag_add("BracketTracker", self.text_widget.index("insert -1c"), "insert")
                return

    def _match_forwards(self, open_char, return_only=False, start_index=None):
        b = 1
        current_index = start_index or self.text_widget.index("insert +1c")

        while True:
            if self.text_widget.compare(current_index, ">=", "end-1c"):
                break  

            word = self.text_widget.get(current_index, f"{current_index} +1c")
            if word == open_char:
                b += 1
            elif word == ")":
                b -= 1
            if b == 0:
                if return_only:
                    return current_index
                self.text_widget.tag_add("BracketTracker", current_index, f"{current_index} +1c")
                self.text_widget.tag_add("BracketTracker", self.text_widget.index("insert"), "insert +1c")
                return
            current_index = self.text_widget.index(f"{current_index} +1c")

    def is_inside_string_or_comment(self,code: str, target_index: int) -> bool:
        try:
            tokens = tokenize.generate_tokens(io.StringIO(code).readline)
            for tok_type, tok_string, (start_line, start_col), (end_line, end_col), _ in tokens:
                if tok_type in (tokenize.STRING, tokenize.COMMENT):
                    if start_col <= target_index < end_col:
                        return True
        except Exception as e:
            pass
        return False