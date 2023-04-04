## @file interpret_tools.py
# @brief Helpful tools of interpret
# @author Marián Tarageľ

from error import Error

def convert(type, value):
    match type:
        case 'int':
            try:
                value = int(value)
            except ValueError:
                Error.handle_error(Error.XML_STRUCT.value)
        case 'bool':
            if value.lower() == 'true': 
                value = True
            else:
                value = False
    return value

def get_var_frame_and_name(var: str) -> tuple[str, str]:
    arg = var.split("@")
    return arg[0], arg[1]

def replace(match):
    return int(match.group(1)).to_bytes(1, byteorder="big")