import re

class BaseLexer:
    """Base class for all language lexers."""
    def __init__(self, editor):
        self.editor = editor
        

    def setup_tags(self):
        """Define all required tags in the editor (colors, fonts)."""
        # Override in subclasses
        pass

    def highlight(self, code=None):
        """Apply syntax highlighting to the code."""
        # Override in subclasses
        raise NotImplementedError("Subclasses must implement highlight()")
