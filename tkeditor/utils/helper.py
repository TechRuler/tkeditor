from tkinter.font import Font 
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