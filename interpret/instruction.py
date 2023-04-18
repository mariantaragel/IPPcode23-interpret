## @file instruction.py
# @brief Instruction representation
# @author Marián Tarageľ

from error import Error

class Instruction:

    opcode: str
    args: list
    order: int

    def __init__(self, opcode: str, order: int):
        self.opcode = opcode
        self.args = []
        self.order = order

    # Add one argument
    def add_arg(self, arg: object) -> None:
        self.args.insert(arg.position, arg)

    # Add al arguments
    def add_args(self, arg1: object, arg2: object, arg3: object) -> None:
        if arg1 == None and arg2 != None:
            Error.handle_error(Error.XML_STRUCT.value)
        if (arg1 == None or arg2 == None) and arg3 != None:
            Error.handle_error(Error.XML_STRUCT.value)
        
        if arg1 != None:
            self.add_arg(arg1)
        if arg1 != None and arg2 != None:
            self.add_arg(arg2)
        if arg1 != None and arg2 != None and arg3 != None:
            self.add_arg(arg3)