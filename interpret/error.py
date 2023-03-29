## @file error.py
# @brief Error handling
# @author Marián Tarageľ

ERR_ARGS = 10
ERR_IN_FILE = 11
ERR_OUT_FILE = 12
ERR_XML_FORMAT = 31
ERR_XML_STRUCT = 32
ERR_SEMANTIC = 52
ERR_OP_TYPES = 53
ERR_NO_VAR = 54
ERR_NO_FRAME = 55
ERR_MISSING_VAL = 56
ERR_OP_VAL = 57
ERR_STRING = 58

class Error:
    
    @staticmethod
    def handle_error(error_code: int):
        print('Error: ' + str(error_code))
        exit(error_code)