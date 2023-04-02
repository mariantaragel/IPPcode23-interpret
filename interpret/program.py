## @file program.py
# @brief Program representation
# @author Marián Tarageľ

from instruction import Instruction
from argument import Argument
from error import Error
import re

class Program:

    instructions: list
    labels: list
    global_frame: dict
    local_frame: dict
    temporary_frame: dict

    def __init__(self):
        self.instructions = []
        self.labels = []
        self.global_frame = {}
        self.local_frame = None
        self.temporary_frame = None

    def add_instruction_to_program(self, instruction: object) -> None:
        if instruction.opcode == 'LABEL':
            self.labels.append(instruction.args[0].value)
        self.instructions.append(instruction)

    def sort_instructions(self) -> None:
        self.instructions.sort(key=lambda instruction: instruction.order)

    def get_instruction(self):
        if len(self.instructions) > 0:
            return self.instructions.pop(0)
        else:
            return None
        
    def get_program_from_xml(self, tree: object) -> None:
        for child in tree:
            opcode = child.attrib.get('opcode').upper()
            order = child.attrib.get('order')
            instruction = Instruction(opcode, int(order))
        
            for subchild in child:
                type = subchild.attrib.get('type')
                value = subchild.text
                if value == None:
                    value = ""
                argument = Argument(type, value)
                instruction.add_arg(argument)

            self.add_instruction_to_program(instruction)

    @staticmethod
    def get_var_frame_and_name(var: str) -> tuple[int, int]:
        arg = var.split("@")
        return arg[0], arg[1]
    
    def is_var_in_frame(self, var_name: str, frame: str) -> bool:
        if frame == 'GF':
            if var_name in self.global_frame:
                return True
            else:
                return False
        elif frame == 'LF':
            if var_name in self.local_frame:
                return True
            else:
                return False
        elif frame == 'TF':
            if var_name in self.temporary_frame:
                return True
            else:
                return False

    def interpret_defvar(self, instruction: object) -> None:
        frame, var_name = self.get_var_frame_and_name(instruction.args[0].value)

        if self.is_var_in_frame(var_name, frame) == False:
            self.global_frame[var_name] = None
        else:
            Error.handle_error(Error.SEMANTIC.value)

    def interpret_move(self, instruction: object) -> None:
        frame_to, var_name_to = self.get_var_frame_and_name(instruction.args[0].value)
        type = instruction.args[1].type
        value = instruction.args[1].value
        
        if type == 'var':
            frame_from, var_name_from = self.get_var_frame_and_name(value)
            if self.is_var_in_frame(var_name_from, frame_from) == False:
                Error.handle_error(Error.NO_VAR.value)
            else:
                value = self.global_frame.get(var_name_from)
        
        if self.is_var_in_frame(var_name_to, frame_to) == True:
            self.global_frame[var_name_to] = value
        else:
            Error.handle_error(Error.NO_VAR.value)

    @staticmethod
    def replace(match):
        a = hex(int(match.group(0)))
        b = re.sub('x', '', a)
        return "\\" + b;

    def interpret_write(self, instruction: object) -> None:
        new = re.sub('\d{3}', self.replace, instruction.args[0].value)
        print(new)