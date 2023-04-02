## @file instruction.py
# @brief Instruction representation
# @author Marián Tarageľ

class Instruction:

    opcode: str
    args: list
    order: int

    def __init__(self, opcode: str, order: int):
        self.opcode = opcode
        self.args = []
        self.order = order

    def add_arg(self, arg: object) -> None:
        self.args.insert(arg.position, arg)