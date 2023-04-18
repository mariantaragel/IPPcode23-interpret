## @file interpret_tools.py
# @brief Helpful tools of interpret
# @author Marián Tarageľ

def convert(type, value):
    match type:
        case 'int':
            try:
                value = int(value.strip())
            except ValueError:
                value = None
        case 'bool':
            if value == '':
                value = None
            elif value.lower().strip() == 'true': 
                value = True
            else:
                value = False
        case 'var':
            value = value.strip()
    return value

# Return variable frame and names
def get_var_frame_and_name(var: str) -> tuple[str, str]:
    arg = var.split("@")
    return arg[0], arg[1]

# Replace escape sequnce
def replace(match):
    return int(match.group(1)).to_bytes(1, byteorder="big")