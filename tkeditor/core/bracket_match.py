import tokenize
import io
class BracketTracker:
    def __init__(self, text_widget, color=None):
        self.text_widget = text_widget
        self.open_brackets = {
            '(': ')',
            '{': '}',
            '[': ']'
        }
        self.close_brackets = {
            ')': '(',
            '}': '{',
            ']': '['
        }
        bgcolor = color if color else 'lightblue'
        self.text_widget.tag_configure("BracketTracker", background = bgcolor)
        self.text_widget.tag_lower("BracketTracker")
        self.text_widget.tag_raise("sel")

        # self.text_widget.bind("<KeyRelease>", lambda e:self.track_brackets(), add="+")
        # self.text_widget.bind("<Button-1>", lambda e: self.text_widget.after_idle(self.track_brackets), add="+")
    def set_color(self, color):
        """Set the color for bracket tracking."""
        self.text_widget.tag_configure("BracketTracker", background = color)
    # def track_brackets(self):
    #     self.text_widget.tag_remove("BracketTracker", "1.0", "end")

    #     cursor_index = self.text_widget.index("insert")
    #     line = self.text_widget.get("insert linestart", "insert lineend")
    #     col = int(cursor_index.split(".")[1])

    #     # Do not stop here — we only skip brackets *inside* strings/comments
    #     pre_word = self.text_widget.get("insert -1c", "insert")
    #     after_word = self.text_widget.get("insert", "insert +1c")

    #     try:
    #         if pre_word in self.close_brackets.keys():
    #             self._match_backwards(pre_word)
    #         elif after_word in self.open_brackets.keys():
    #             self._match_forwards(after_word)
    #         else:
    #             # Handle case where cursor is BETWEEN matching ()
    #             # like:   (|)  ← cursor is between
    #             prev = self.text_widget.get("insert -1c", "insert")
    #             next = self.text_widget.get("insert", "insert +1c")
    #             if prev in self.open_brackets.keys() and next == self.open_brackets[prev]:
    #                 # Check that neither bracket is inside string/comment
    #                 line = self.text_widget.get("insert linestart", "insert lineend")
    #                 col = int(self.text_widget.index("insert").split(".")[1])
    #                 if not self.is_inside_string_or_comment(line, col - 1) and not self.is_inside_string_or_comment(line, col):
    #                     self.text_widget.tag_add("BracketTracker", "insert -1c", "insert")
    #                     self.text_widget.tag_add("BracketTracker", "insert", "insert +1c")
    #             else:
    #                 nearest = None  # (index, close_bracket)

    #                 # Search backwards to find the closest closing bracket
    #                 for close_bracket in self.close_brackets:
    #                     index = self._match_backwards(close_bracket, return_only=True)
    #                     if index:
    #                         if (nearest is None) or (self.text_widget.compare(index, ">", nearest[0])):
    #                             nearest = (index, close_bracket)

    #                 if nearest:
    #                     open_index, close_char = nearest
    #                     open_char = self.close_brackets[close_char]

    #                     self.text_widget.mark_set("match_temp", open_index)
    #                     close_index = self._match_forwards(open_char, return_only=True, start_index="match_temp +1c")

    #                     if close_index:
    #                         self.text_widget.tag_add("BracketTracker", open_index, f"{open_index} +1c")
    #                         self.text_widget.tag_add("BracketTracker", close_index, f"{close_index} +1c")
    #     except Exception as e:
    #         print("Bracket track error:", e)
    def track_brackets(self):
        self.text_widget.tag_remove("BracketTracker", "1.0", "end")

        cursor = self.text_widget.index("insert")

        prev_char = self.text_widget.get("insert -1c", "insert")
        next_char = self.text_widget.get("insert", "insert +1c")

        
        if next_char in self.open_brackets:
            self._match_forwards(next_char)
            return

        
        if prev_char in self.close_brackets:
            self._match_backwards(prev_char, start_index="insert -1c")
            return

        
        if prev_char in self.open_brackets and next_char == self.open_brackets[prev_char]:
            line = self.text_widget.get("insert linestart", "insert lineend")
            col = int(self.text_widget.index("insert").split(".")[1])
            if not self.is_inside_string_or_comment(line, col-1) and not self.is_inside_string_or_comment(line, col):
                self.text_widget.tag_add("BracketTracker", "insert -1c", "insert")
                self.text_widget.tag_add("BracketTracker", "insert", "insert +1c")
            return

    def _match_backwards(self, close_char, return_only=False, start_index=None):
        open_char = self.close_brackets.get(close_char)
        current_index = start_index or self.text_widget.index("insert -1c")

        depth = 1
        while True:
            # Search backwards for either char
            idx = self.text_widget.search(f"[{close_char}{open_char}]", current_index, stopindex="1.0", backwards=True, regexp=True)
            if not idx:
                return None

            ch = self.text_widget.get(idx, f"{idx} +1c")
            if ch == close_char:
                depth += 1
            elif ch == open_char:
                depth -= 1

            if depth == 0:
                if return_only:
                    return idx
                self.text_widget.tag_add("BracketTracker", idx, f"{idx} +1c")
                self.text_widget.tag_add("BracketTracker", self.text_widget.index("insert -1c"), "insert")
                return

            current_index = idx

    def _match_forwards(self, open_char, return_only=False, start_index=None):
        close_char = self.open_brackets.get(open_char)
        current_index = start_index or self.text_widget.index("insert +1c")

        depth = 1
        while True:
            # Search forwards for either char
            idx = self.text_widget.search(f"[{open_char}{close_char}]", current_index, stopindex="end-1c", forwards=True, regexp=True)
            if not idx:
                return None

            ch = self.text_widget.get(idx, f"{idx} +1c")
            if ch == open_char:
                depth += 1
            elif ch == close_char:
                depth -= 1

            if depth == 0:
                if return_only:
                    return idx
                self.text_widget.tag_add("BracketTracker", idx, f"{idx} +1c")
                self.text_widget.tag_add("BracketTracker", self.text_widget.index("insert"), "insert +1c")
                return

            current_index = f"{idx} +1c"


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