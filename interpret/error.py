## @file error.py
# @brief Error handling
# @author Marián Tarageľ

from enum import Enum

class Error(Enum):
    
    ARGS = 10
    IN_FILE = 11
    OUT_FILE = 12
    XML_FORMAT = 31
    XML_STRUCT = 32
    SEMANTIC = 52
    OP_TYPES = 53
    NO_VAR = 54
    NO_FRAME = 55
    MISSING_VAL = 56
    OP_VAL = 57
    STRING = 58

    @staticmethod
    # Handle error states
    def handle_error(error_code: int):
        exit(error_code)