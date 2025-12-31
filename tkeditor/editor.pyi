from typing import Any, Optional, Callable, Literal
from tkinter import Frame, Misc
from tkeditor.core import CustomText
from tkeditor.ui import LineNumber, AutoScrollbar, FoldingCode, ContextMenu


class Editor(Frame):
    _line_number: LineNumber
    _folding_code: FoldingCode
    _text: CustomText
    _v_scroll: AutoScrollbar
    _h_scroll: AutoScrollbar
    _context_menu: ContextMenu
    _style: Any

    def __init__(
        self,
        master: Optional[Misc] = None,
        *,
        # ---- Frame options ----
        background: str = ...,
        bg: str = ...,
        bd: float | str = ...,
        border: float | str = ...,
        borderwidth: float | str = ...,
        relief: Literal['flat', 'raised', 'sunken', 'ridge', 'solid', 'groove'] = ...,
        class_: str = ...,
        colormap: Misc | Literal['new', ''] = ...,
        container: bool = ...,
        cursor: str = ...,
        height: float | str = ...,
        name: str = ...,
        padx: float | str = ...,
        pady: float | str = ...,
        takefocus: bool | int | str = ...,
        visual: str | tuple[str, int] = ...,
        width: float | str = ...,

        # ---- Text options ----
        autoseparators: bool = ...,
        blockcursor: bool = ...,
        endline: int | str = ...,
        exportselection: bool = ...,
        fg: str = ...,
        font: str | tuple = ...,
        foreground: str = ...,
        inactiveselectbackground: str = ...,
        insertbackground: str = ...,
        insertborderwidth: float | str = ...,
        insertofftime: int = ...,
        insertontime: int = ...,
        insertunfocussed: Literal['none', 'hollow', 'solid'] = ...,
        insertwidth: float | str = ...,
        maxundo: int = ...,
        selectbackground: str = ...,
        selectborderwidth: float | str = ...,
        selectforeground: str = ...,
        setgrid: bool = ...,
        spacing1: float | str = ...,
        spacing2: float | str = ...,
        spacing3: float | str = ...,
        startline: int | str = ...,
        state: Literal['normal', 'disabled'] = ...,
        tabs: float | str | tuple[float | str, ...] = ...,
        tabstyle: Literal['tabular', 'wordprocessor'] = ...,
        undo: bool = ...,
        wrap: Literal['none', 'char', 'word'] = ...,
        
        # ---- Editor-specific ----
        scrollbg: str = ...,
        thumbbg: str = ...,
        activescrollbg: str = ...,

        folder_code: bool = ...,
        linenumber: bool = ...,
        indentationguide: bool = ...,

        indent_line_color: str = ...,
        line_number_fg: str = ...,
        lineboxwidth: int = ...,

        folding_arrow_color: str = ...,
        foldingboxwidth: int = ...,
        folding_bg: str = ...,

        bracket_tracker: bool = ...,
        bracket_tracker_color: str = ...,
        current_line_color: str = ...,

        **kwargs: Any
    ) -> None: ...

    def create_scrollbar_style(
        self, 
        name: str, 
        trough_color: str, 
        thumb_color: str, 
        hover_color: str
    ) -> None: ...

    def scrollbar_layout(self) -> None: ...
    def debounce(self, widget: Any, attr_name: str, delay: int, callback: Callable[..., Any]) -> None: ...
    def Events(self, **kwarg: Any) -> None: ...

    def line_number_config(
        self,
        *,
        # ---- Canvas options ----
        background: str = ...,
        bg: str = ...,
        bd: float | str = ...,
        border: float | str = ...,
        borderwidth: float | str = ...,
        closeenough: float = ...,
        confine: bool = ...,
        cursor: str = ...,
        height: float | str = ...,
        highlightbackground: str = ...,
        highlightcolor: str = ...,
        highlightthickness: float | str = ...,
        insertbackground: str = ...,
        insertborderwidth: float | str = ...,
        insertofftime: int = ...,
        insertontime: int = ...,
        insertwidth: float | str = ...,
        offset: str = ...,
        relief: Literal['flat', 'raised', 'sunken', 'ridge', 'solid', 'groove'] = ...,
        scrollregion: str | tuple[int, int, int, int] = ...,
        selectbackground: str = ...,
        selectborderwidth: float | str = ...,
        selectforeground: str = ...,
        state: Literal['normal', 'disabled', 'hidden'] = ...,
        takefocus: bool | int | str = ...,
        width: float | str = ...,
        
        # ---- LineNumber-specific ----
        fg: str = ...,
        current_line_number:str =...,
        font: str | tuple = ...,
       

        **kwargs: Any
    ) -> None: ...

    
    def folding_code_config(
        self,
        *,
        # ---- Canvas options ----
        background: str = ...,
        bg: str = ...,
        bd: float | str = ...,
        border: float | str = ...,
        borderwidth: float | str = ...,
        closeenough: float = ...,
        confine: bool = ...,
        cursor: str = ...,
        height: float | str = ...,
        highlightbackground: str = ...,
        highlightcolor: str = ...,
        highlightthickness: float | str = ...,
        insertbackground: str = ...,
        insertborderwidth: float | str = ...,
        insertofftime: int = ...,
        insertontime: int = ...,
        insertwidth: float | str = ...,
        offset: str = ...,
        relief: Literal['flat', 'raised', 'sunken', 'ridge', 'solid', 'groove'] = ...,
        scrollregion: str | tuple[int, int, int, int] = ...,
        selectbackground: str = ...,
        selectborderwidth: float | str = ...,
        selectforeground: str = ...,
        state: Literal['normal', 'disabled', 'hidden'] = ...,
        takefocus: bool | int | str = ...,
        width: float | str = ...,
        
        

        # ---- FoldingCode-specific ----
        fg: str = ...,
        symbols: list | tuple = ...,
        font: str | tuple = ...,

        **kwargs: Any
    ) -> None: ...


    def configure(
        self,
        # ---- Frame options ----
        background: str = ...,
        bg: str = ...,
        bd: float | str = ...,
        border: float | str = ...,
        borderwidth: float | str = ...,
        relief: Literal['flat', 'raised', 'sunken', 'ridge', 'solid', 'groove'] = ...,
        class_: str = ...,
        colormap: Misc | Literal['new', ''] = ...,
        container: bool = ...,
        cursor: str = ...,
        height: float | str = ...,
        highlightbackground: str = ...,
        highlightcolor: str = ...,
        highlightthickness: float | str = ...,
        name: str = ...,
        padx: float | str = ...,
        pady: float | str = ...,
        takefocus: bool | int | str = ...,
        visual: str | tuple[str, int] = ...,
        width: float | str = ...,

        # ---- Text options ----
        autoseparators: bool = ...,
        blockcursor: bool = ...,
        endline: int | str = ...,
        exportselection: bool = ...,
        fg: str = ...,
        font: str | tuple = ...,
        foreground: str = ...,
        inactiveselectbackground: str = ...,
        insertbackground: str = ...,
        insertborderwidth: float | str = ...,
        insertofftime: int = ...,
        insertontime: int = ...,
        insertunfocussed: Literal['none', 'hollow', 'solid'] = ...,
        insertwidth: float | str = ...,
        maxundo: int = ...,
        selectbackground: str = ...,
        selectborderwidth: float | str = ...,
        selectforeground: str = ...,
        setgrid: bool = ...,
        spacing1: float | str = ...,
        spacing2: float | str = ...,
        spacing3: float | str = ...,
        startline: int | str = ...,
        state: Literal['normal', 'disabled'] = ...,
        tabs: float | str | tuple[float | str, ...] = ...,
        tabstyle: Literal['tabular', 'wordprocessor'] = ...,
        undo: bool = ...,
        wrap: Literal['none', 'char', 'word'] = ...,
        xscrollcommand: Optional[Callable[[float, float], Any]] = ...,
        yscrollcommand: Optional[Callable[[float, float], Any]] = ...,

        # ---- Editor-specific ----
        scrollbg: str = ...,
        thumbbg: str = ...,
        activescrollbg: str = ...,

        folder_code: bool = ...,
        linenumber: bool = ...,
        indentationguide: bool = ...,

        indent_line_color: str = ...,
        line_number_fg: str = ...,
        lineboxwidth: int = ...,

        folding_arrow_color: str = ...,
        foldingboxwidth: int = ...,
        folding_bg: str = ...,

        bracket_tracker: bool = ...,
        bracket_tracker_color: str = ...,
        current_line_color: str = ...,

        **kwargs: Any
    ) -> None: ...
    config = configure

    def bind(
        self,
        widget:str =...,
        sequence: Optional[str] = ..., 
        func: Optional[Callable[..., Any]] = ..., 
        add: Optional[str] = ...
    ) -> None: ...

    def get_context_menu(self) -> ContextMenu: ...
    def get_content(self, condition: str) -> Any: ...
    def get_text_widget(self) -> CustomText: ...
    def get_line_number_widget(self) -> LineNumber:...
    def get_folding_code_widget(self) -> FoldingCode:...
