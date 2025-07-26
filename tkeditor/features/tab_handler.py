class TabHandler:
    def setup_tab_handler(self):
        self.bind("<Tab>", self._handle_tab, add="+")

    def set_tabWidth(self, width:int):
        """Set the tab width for the editor."""
        if isinstance(width, int) and width >= 0:
            if width > 0:
                self.tab_width = width
            else:
                raise ValueError("Tab width must be a positive integer.")
        else:
            raise TypeError("Tab width must be an integer.")
        
    def _handle_tab(self, event):
        """Handle tab key press for indentation."""
        self.insert("insert", " " * self.tab_width)
        return "break"
