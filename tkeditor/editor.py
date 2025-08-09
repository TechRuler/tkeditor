from tkinter import Frame
from tkeditor.core import CustomText
from tkeditor.components import LineNumber, AutoScrollbar, FoldingCode, ContextMenu
from tkinter import ttk 
class Editor(Frame):
    def __init__(self, master, **kwarg):
        """
        A subclass of `tk.Text` that supports all standard `Text` parameters,
        plus additional options for enhanced code editing features.

        Additional Parameters:
            **scrollbg (str)**: Background color of the scrollbar trough.
            **thumbbg (str)**: Background color of the scrollbar thumb.
            **activescrollbg (str)**: Background color of the scrollbar thumb when active/hovered.
            **folder_code (bool)**: Enables or disables code folding.
            **linenumber (bool)**: Enables or disables the display of line numbers.
            **indent_line_color (str)**: Color of vertical indentation guide lines.
            **line_number_fg (str)**: Foreground (text) color of line numbers.
            **lineboxwidth (int)**: Width of the line number gutter in pixels.
            **folding_arrow_color (str)**: Color of the code-folding arrow indicator.
            **foldingboxwidth (int)**: Width of the folding gutter in pixels.
            **folding_bg (str)**: Background color of the folding gutter.
            **bracket_tracker_color (str)**: Highlight color for matching brackets.
            **current_line_color (str)**: Background color for the current line highlight.
        """

        Allowed_keys = Frame(master).keys()
        super().__init__(master, **{k:v for k, v in kwarg.items() if k in Allowed_keys})
        self.master = master

        self.scrollbar_layout()
        

        self.line_number = LineNumber(self, **kwarg)
        self.folding_code = FoldingCode(self, **kwarg)
        self.text  = CustomText(self, **kwarg)
        self.v_scroll = AutoScrollbar(self, orient='vertical', command=self.text.yview, style='Custom.Vertical.TScrollbar')
        self.h_scroll = AutoScrollbar(self, orient='horizontal', command=self.text.xview, style='Custom.Horizontal.TScrollbar')

        self.text.config(yscrollcommand=self.v_scroll.set)
        self.text.config(xscrollcommand=self.h_scroll.set)


        self.line_number.attach(self.text)
        self.folding_code.attach(self.text)


        trough_color = kwarg.get('scrollbg') if kwarg.get('scrollbg') else self.text.cget('bg')
        thumb_color = kwarg.get('thumbbg') if kwarg.get('thumbbg') else "#5b5b5b"
        hover_color = kwarg.get('activescrollbg') if kwarg.get('activescrollbg') else self.text.cget('bg')
        self.create_scrollbar_style("Custom.Vertical.TScrollbar",trough_color=trough_color, thumb_color=thumb_color,hover_color=hover_color)
        self.create_scrollbar_style("Custom.Horizontal.TScrollbar",trough_color=trough_color, thumb_color=thumb_color,hover_color=hover_color)


        self.text.grid(row=0, column=2, sticky='nsew')
        self.v_scroll.grid(row=0, column=3, rowspan=2, sticky='ns')
        self.h_scroll.grid(row=1, column=2, sticky='ew')
        if kwarg.get('folding_code', True):
            self.folding_code.grid(row=0, column=1, rowspan=2, sticky='ns')
        if kwarg.get('linenumber',True):
            self.line_number.grid(row=0, column=0, rowspan=2, sticky='ns')

        self.rowconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)
        
        
        self.context_menu = ContextMenu(self.text)
        self.context_menu.setup_context_menu()


        self.Events(**kwarg)
    
    def create_scrollbar_style(self,name: str, trough_color: str,thumb_color: str, hover_color: str):
        self.style.configure(name,
                        troughcolor=trough_color,
                        background=thumb_color,
                        bordercolor=trough_color,
                        lightcolor=thumb_color,
                        darkcolor=thumb_color,
                        arrowcolor=thumb_color,
                        gripcount=0)

        
        self.style.map(name, background=[('active', hover_color)])
    def scrollbar_layout(self):
        self.style = ttk.Style(self.master)
        self.style.theme_use('clam')
        self.style.layout('Custom.Vertical.TScrollbar', [
            ('Vertical.Scrollbar.trough', {
                'children': [
                    ('Vertical.Scrollbar.thumb', {'unit': '1', 'sticky': 'ns'})
                ],
                'sticky': 'ns'
            })
        ])
        self.style.layout('Custom.Horizontal.TScrollbar', [
            ('Horizontal.Scrollbar.trough', {
                'children': [
                    ('Horizontal.Scrollbar.thumb', {'unit': '1', 'sticky': 'ew'})
                ],
                'sticky': 'ew'
            })
        ])

    # def Events(self, **kwarg):
    #     # bracket tracker events
    #     self.text.bind("<KeyRelease>", lambda e:self.text.bracket_tracker.track_brackets(), add="+")
    #     self.text.bind("<Button-1>", lambda e: self.text.after_idle(self.text.bracket_tracker.track_brackets), add="+")

    #     # folding code events
    #     for event in ("<Configure>", "<KeyRelease>", "<MouseWheel>", "<ButtonRelease-1>"):
    #         self.text.bind(event, self.folding_code._schedule_draw, add="+")
    #     self.folding_code.bind("<Button-1>", self.folding_code._on_click)
    
    #     # line number events
    #     for event in ("<KeyRelease>", "<MouseWheel>", "<Button-1>", "<Configure>"):
    #         self.text.bind(event, self.line_number.schedule_redraw, add="+")


    #     # intentation and auto-indent
    #     self.text.bind("<Return>", self.text.indent.auto_indent, add="+")
    #     self.text.bind("<Control-Return>", self.text.indent.escape_line, add="+")
    #     self.text.bind("<BackSpace>", self.text.indent.backspace, add="+")

    #     # base editor events
    #     for key in ["[", "{", "(", "]", "}", ")", "'", '"']:
    #         self.text.bind(f"<Key-{key}>", self.text.brackets_and_string_complete, add="+")
    #     self.text.bind("<Tab>", self.text._handle_tab, add="+")
    #     self.text.bind("<Button-1>", self.text.set_current_line_color, add="+")
    #     self.text.bind("<Key>", self.text.set_current_line_color, add="+")
    #     self.text.bind("<B1-Motion>", lambda e: self.text.tag_remove('current_line','1.0','end'), add="+")

    #     # editor events
    #     self.v_scroll.bind("<B1-Motion>", self._on_key_release, add="+")
    #     self.h_scroll.bind("<B1-Motion>", self._on_key_release, add="+")
    #     if kwarg.get('indentationguide',False):
    #         self.folding_code.bind("<Button-1>", self.text.indentationguide.schedule_draw, add="+")
    #     self.folding_code.bind("<Button-1>", self._on_key_release, add="+")
    def debounce(self, widget, attr_name, delay, callback):
        after_id = getattr(widget, attr_name, None)
        if after_id:
            widget.after_cancel(after_id)
        setattr(widget, attr_name, widget.after(delay, callback))

    def Events(self, **kwarg):
        ### --- Bracket Tracker --- ###
        self.text.bind("<KeyRelease>", lambda e: self.debounce(self.text, "_track_bracket_after", 50, self.text.bracket_tracker.track_brackets), add="+")
        self.text.bind("<Button-1>", lambda e: self.text.after_idle(self.text.bracket_tracker.track_brackets), add="+")

        ### --- Folding Code --- ###
        def fold(): self.folding_code._schedule_draw()
        for event in ("<Configure>", "<KeyRelease>", "<MouseWheel>", "<ButtonRelease-1>"):
            self.text.bind(event, lambda e: self.debounce(self.text, "_folding_after", 100, fold), add="+")
        self.v_scroll.bind("<B1-Motion>", lambda e: self.debounce(self.text, "_folding_after", 100, fold), add="+")
        self.folding_code.bind("<Button-1>", self.folding_code._on_click, add="+")

        ### --- Line Number --- ###
        def redraw_lines(): self.line_number.schedule_redraw()
        for event in ("<KeyRelease>", "<MouseWheel>", "<Button-1>", "<Configure>"):
            self.text.bind(event, lambda e: self.debounce(self.text, "_line_after", 50, redraw_lines), add="+")
        self.text.bind("<<Redraw>>", self.line_number.schedule_redraw)

        ### --- Indentation Events --- ###
        self.text.bind("<Return>", self.text.indent.auto_indent, add="+")
        self.text.bind("<Control-Return>", self.text.indent.escape_line, add="+")
        self.text.bind("<BackSpace>", self.text.indent.backspace, add="+")

        ### --- Bracket Completion --- ###
        for key in ["[", "{", "(", "]", "}", ")", "'", '"']:
            self.text.bind(f"<Key-{key}>", self.text.brackets_and_string_complete, add="+")

        ### --- Tab Key --- ###
        self.text.bind("<Tab>", self.text._handle_tab, add="+")

        ### --- Current Line Highlight --- ###
        def highlight_line():
            self.debounce(self.text, "_linecolor_after", 50, self.text.set_current_line_color)

        self.text.bind("<Key>", lambda e: highlight_line(), add="+")
        self.text.bind("<Button-1>", lambda e: highlight_line(), add="+")
        self.text.bind("<B1-Motion>", lambda e: self.text.tag_remove('current_line', '1.0', 'end'), add="+")

        ### --- Scroll Triggers --- ###
        self.v_scroll.bind("<B1-Motion>", self._on_key_release, add="+")
        self.h_scroll.bind("<B1-Motion>", self._on_key_release, add="+")

        ### --- Optional Indentation Guide Trigger --- ###
        if kwarg.get('indentationguide', False):
            self.folding_code.bind("<Button-1>", lambda e: self.text.indentationguide.schedule_draw(), add="+")

        self.folding_code.bind("<Button-1>", self._on_key_release, add="+")


    def configure(self, **kwarg):
        super().configure(**{k:v for k, v in kwarg.items() if k in Frame().keys()})
        if "linenumber" in kwarg.keys():
            if kwarg.get('linenumber'):
                self.line_number.grid(row=0, column=0,rowspan=2, sticky='ns')
            else:
                self.line_number.grid_remove()

        if "folding_code" in kwarg.keys():
            if kwarg.get('folding_code'):
                self.folding_code.grid(row=0, column=1, rowspan=2, sticky='ns')
            else:
                self.folding_code.grid_remove()

        self.text.configure(**kwarg)
        self.line_number.configure(**kwarg)
        self.folding_code.configure(**kwarg)

        if  'indent_line_color' in kwarg.keys():
            self.text.indentationguide.set_color(kwarg.get('indent_line_color', '#4b4b4b'))

        if 'folding_arrow_color' in kwarg.keys():
            self.folding_code.set_color(kwarg.get('folding_arrow_color', '#aaa'))

        if 'bracket_tracker_color' in kwarg.keys():
            self.text.bracket_tracker.set_color(kwarg.get('bracket_tracker_color','lightblue'))

        trough_color = kwarg.get('scrollbg') if kwarg.get('scrollbg') else self.text.cget('bg')
        thumb_color = kwarg.get('thumbbg') if kwarg.get('thumbbg') else "#5b5b5b"
        hover_color = kwarg.get('activescrollbg') if kwarg.get('activescrollbg') else self.text.cget('bg')
        self.create_scrollbar_style("Custom.Vertical.TScrollbar",
                                       trough_color=trough_color, 
                                       thumb_color=thumb_color,
                                       hover_color=hover_color
                                       )
        self.create_scrollbar_style("Custom.Horizontal.TScrollbar",
                                       trough_color=trough_color, 
                                       thumb_color=thumb_color,
                                       hover_color=hover_color
                                       )
    config = configure
        
    def set_lexer(self, lexer_instance):
        """Accept a lexer object and set up highlighting."""
        self.lexer = lexer_instance
        self.lexer.setup_tags()
        self.text.bind("<KeyRelease>", self._on_key_release, add="+")
        self.text.bind("<Configure>", self._on_key_release, add="+")
        self.text.bind("<MouseWheel>", self._on_key_release, add="+")
        self.text.bind("<Button-1>", self._on_key_release, add="+")
        self._on_key_release()

    
    def _on_key_release(self, event=None):
        """Callback to update highlighting after key press."""
        if hasattr(self, 'lexer'):
            self.lexer.highlight()


    def bind(self, sequence=None, func=None, add=None):
        self.text.bind(sequence, func, add)
    def get_context_menu(self):
        """Return the context menu for the editor."""
        return self.text.context_menu.get_popup_menu()