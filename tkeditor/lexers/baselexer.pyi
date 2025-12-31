from typing import Dict, TypedDict, List, Tuple
from typing_extensions import Unpack

class Style(TypedDict, total=False):
    foreground: str
    background: str
    font: str
class StyleKeywords(TypedDict, total=False):
    ident: Style
    keyword: Style
    builtin: Style
    function: Style
    class_: Style
    operator: Style
    number: Style
    string: Style
    f_expr: Style
    comment: Style
    decorator: Style

    tag: Style
    attribute: Style
    value: Style

    property: Style
    selector: Style
    unit: Style

    preprocessor: Style

Styles = Dict[str, Style]

class BaseLexer:
    name: str
    file_extensions: List[str]
    default_styles: Styles
    styles: Styles

    def __init__(self) -> None: ...

    def set_styles(
        self,
        styles: Styles | None = ...,
        **kwargs: Unpack[StyleKeywords]
    ) -> None: ...

    def get_styles(self) -> Styles: ...

    def lex(self, text: str) -> List[Tuple[str, str, str]]: ...
