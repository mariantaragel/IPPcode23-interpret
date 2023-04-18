## @file argument.py
# @brief Argument representation
# @author Marián Tarageľ

class Argument:

    type: str
    value: str
    position: int

    def __init__(self, type: str, value: str):
        self.type = type
        self.value = value
        self.position = 0

    # Add argument number
    def add_argument_position(self, tag):
        match tag:
            case 'arg1':
                self.position = 0
            case 'arg2':
                self.position = 1
            case 'arg3':
                self.position = 2