from tkinter.font import Font 
import importlib.util
import os
# from tkeditor.lexers.base_lexer import BaseLexer
def get_font(font):
    font_dict = {}
    if isinstance(font, (tuple,list)):
        for item in font:
            if item in ['normal', 'bold']:
                font_dict['weight'] = item 
            elif item in ['roman', 'italic']:
                font_dict['slant'] = item 
            elif isinstance(item, int):
                font_dict['size'] = item 
            elif isinstance(item, str) and item not in ['normal', 'bold', 'roman', 'italic']:
                font_dict['family'] = item
    else:
        font_dict['family'] = font
    try:
        return Font(**font_dict)
    except Exception as e:
        print("font error :", e)


# def load_lexer(file_path: str, class_name: str, editor):
#     if not os.path.isfile(file_path):
#         raise FileNotFoundError(f"Lexer file not found: {file_path}")

#     spec = importlib.util.spec_from_file_location("user_lexer", file_path)
#     module = importlib.util.module_from_spec(spec)
#     spec.loader.exec_module(module)

#     LexerClass = getattr(module, class_name, None)
#     if not LexerClass:
#         raise AttributeError(f"No class named {class_name} found in {file_path}")
#     if not issubclass(LexerClass, BaseLexer):
#         raise TypeError(f"{class_name} must inherit from BaseLexer")

#     return LexerClass(editor)
