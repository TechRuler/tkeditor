# tkeditor

**tkeditor** is a modern, extensible Tkinter-based code editor framework written in pure Python.  
It is designed for building IDE-like applications with syntax highlighting, folding, line numbers, and deep customization.

Unlike basic Tkinter text widgets, **tkeditor focuses on performance, flexibility, and developer control**.

## Features

- Custom lexer system (BaseLexer API)
- Language-agnostic syntax highlighting
- Fully customizable token styles
- Canvas-based line numbers
- Current line highlighting
- Code folding with symbols
- Bracket tracking
- Indentation guides
- Custom scrollbars
- Exposed Frame, Text, and Canvas configuration
- Full .pyi type-hint support for IDE autocomplete

## Installation

### Using pip

```
pip install tkeditor
```
### Using uv
```
uv add tkeditor
```


## Quick Example

```python
import tkinter as tk
from tkeditor import Editor

root = tk.Tk()
root.title("tkeditor demo")

editor = Editor(
    root,
    linenumber=True,
    folder_code=True,
    wrap="none",
    font=("Consolas", 12),
)

editor.pack(fill="both", expand=True)
root.mainloop()
```

## Syntax highlighting
```python
import tkinter as tk
from tkeditor import Editor
from tkeditor.lexers import PythonLexer,Highlighter

root = tk.Tk()
root.geometry("800x500") 
root.title("tkeditor")
editor = Editor(
    root,
    linenumber=True,
    folder_code=True,
    wrap="none",
    font=("Consolas", 12),
)

editor.pack(expand=True, fill="both")


lexer = PythonLexer()

# set custom syntax colors
# method 1
# lexer.set_styles(
#     keyword={"foreground":"tomato"},
#     builtin={"foreground":"steelblue"}
# )
# method 2 
# lexer.set_styles({
#     "keyword":{"foreground":"tomato"},
#     "builtin":{"foreground":"steelblue"}
#     }
# )
# Note you can also use both methods at same time

highlight = Highlighter(editor.get_text_widget(), lexer)
root.mainloop()

```

## Project Links
- GitHub: https://github.com/TechRuler/tkeditor
- PyPI: https://pypi.org/project/tkeditor/

## License
MIT License



