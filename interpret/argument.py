## @file argument.py
# @brief Argument representation
# @author Marián Tarageľ

class Argument:

    type: str
    value: str

    def __init__(self, type: str, value: str):
        self.type = type
        self.value = value