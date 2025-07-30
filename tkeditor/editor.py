from tkinter import Frame
from tkeditor.core import CustomText
from tkeditor.components import LineNumber, AutoScrollbar, FoldingCode, ContextMenu
from tkinter import ttk 
class Editor(Frame):
    def __init__(self, master, **kwarg):
        super().__init__(master, **{k:v for k, v in kwarg.items() if k in Frame(master).keys()})

        
        self.style = ttk.Style(master)
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

        self.line_number = LineNumber(self, **kwarg)
        self.folding_code = FoldingCode(self, **kwarg)
        self.text  = CustomText(self, **kwarg)
        self.v_scroll = AutoScrollbar(self, orient='vertical', command=self.text.yview, style='Custom.Vertical.TScrollbar')
        self.h_scroll = AutoScrollbar(self, orient='horizontal', command=self.text.xview, style='Custom.Horizontal.TScrollbar')

        self.text.config(yscrollcommand=self.v_scroll.set)
        self.text.config(xscrollcommand=self.h_scroll.set)
        self.master = master


        self.line_number.attach(self.text)
        self.folding_code.attach(self.text)
        trough_color = kwarg.get('scrollbg') if kwarg.get('scrollbg') else self.text.cget('bg')
        thumb_color = kwarg.get('thumbbg') if kwarg.get('thumbbg') else "#5b5b5b"
        hover_color = kwarg.get('activescrollbg') if kwarg.get('activescrollbg') else self.text.cget('bg')
        self.__create_scrollbar_style("Custom.Vertical.TScrollbar",
                                       trough_color=trough_color, 
                                       thumb_color=thumb_color,
                                       hover_color=hover_color
                                       )
        self.__create_scrollbar_style("Custom.Horizontal.TScrollbar",
                                       trough_color=trough_color, 
                                       thumb_color=thumb_color,
                                       hover_color=hover_color
                                       )


        self.folding_code.grid(row=0, column=1, rowspan=2, sticky='ns')
        self.text.grid(row=0, column=2, sticky='nsew')
        self.v_scroll.grid(row=0, column=3, rowspan=2, sticky='ns')
        self.h_scroll.grid(row=1, column=2, sticky='ew')
        if kwarg.get('linenumber',True):
            self.line_number.grid(row=0, column=0, rowspan=2, sticky='ns')

        self.rowconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)

        self.v_scroll.bind("<B1-Motion>", self._on_key_release, add="+")
        self.h_scroll.bind("<B1-Motion>", self._on_key_release, add="+")

        self.folding_code.bind("<Button-1>", self._on_key_release, add="+")
        if kwarg.get('indentationguide',False):
            self.folding_code.bind("<Button-1>", self.text.indentationguide.schedule_draw, add="+")
        self.context_menu = ContextMenu(self.text)
        self.context_menu.setup_context_menu()
    def __create_scrollbar_style(self,name: str,
                           trough_color: str,
                           thumb_color: str,
                           hover_color: str):
        # Default thumb style
        self.style.configure(name,
                        troughcolor=trough_color,
                        background=thumb_color,
                        bordercolor=trough_color,
                        lightcolor=thumb_color,
                        darkcolor=thumb_color,
                        arrowcolor=thumb_color,
                        gripcount=0)

        # On hover (active element)
        self.style.map(name, background=[('active', hover_color)])
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
        self.__create_scrollbar_style("Custom.Vertical.TScrollbar",
                                       trough_color=trough_color, 
                                       thumb_color=thumb_color,
                                       hover_color=hover_color
                                       )
        self.__create_scrollbar_style("Custom.Horizontal.TScrollbar",
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