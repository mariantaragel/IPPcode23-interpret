## @file program.py
# @brief Program representation
# @author Marián Tarageľ

from error import Error
from frames import Frames
import re
import xml_tree
from my_bool import Mybool

class Program:

    instructions: list
    position: int
    labels: dict
    frames = Frames()
    input: str

    def __init__(self, input: str):
        self.instructions = []
        self.position = 0
        self.labels = {}
        self.input = input

    def add_instruction_to_program(self, instruction: object) -> None:
        self.instructions.append(instruction)

    def sort_instructions(self) -> None:
        self.instructions.sort(key=lambda instruction: instruction.order)

    def get_instruction(self):
        if self.position < len(self.instructions):
            return self.instructions[self.position]
        else:
            return None
        
    def get_program_from_xml(self, tree: object) -> None:
        xml_tree.check_program_element(tree)
        for child in tree:
            instruction = xml_tree.check_element_instruction(child)
        
            for subchild in child:
                argument = xml_tree.check_element_arg(subchild)
                instruction.add_arg(argument)

            self.add_instruction_to_program(instruction)

    def prepocessing(self) -> None:
        self.sort_instructions()
        prev_order = -1
        for instruction in self.instructions:
            if prev_order == instruction.order:
                Error.handle_error(Error.XML_STRUCT.value)
            self.if_label_add(instruction)
            prev_order = instruction.order
            self.position += 1

    def if_label_add(self, instruction):
        if instruction.opcode == 'LABEL':
            label_name = instruction.args[0].value
            if label_name not in self.labels:
                self.labels[label_name] = self.position
            else:
                Error.handle_error(Error.SEMANTIC.value)

    @staticmethod
    def get_var_frame_and_name(var: str) -> tuple[str, str]:
        arg = var.split("@")
        return arg[0], arg[1]
    
    @staticmethod
    def replace(match):
        return int(match.group(1)).to_bytes(1, byteorder="big")
    
    def get_val_and_type(self, instruction_arg: object) -> tuple:
        value = instruction_arg.value
        type = instruction_arg.type
        if type == 'var':
            frame, var_name = self.get_var_frame_and_name(instruction_arg.value)
            var = self.frames.get_var(var_name, frame)
            value = var.value
            type = var.type
        return value, type

    def interpret_defvar(self, instruction: object) -> None:
        if len(instruction.args) != 1:
            Error.handle_error(Error.XML_STRUCT.value)
        frame, var_name = self.get_var_frame_and_name(instruction.args[0].value)
        self.frames.def_var(var_name, frame)

    def interpret_move(self, instruction: object) -> None:
        if len(instruction.args) != 2:
            Error.handle_error(Error.XML_STRUCT.value)
        frame, var_name = self.get_var_frame_and_name(instruction.args[0].value)
        value, type = self.get_val_and_type(instruction.args[1])
        self.frames.set_var(var_name, frame, value, type)

    # TODO: špecialny prípad type == bool (viz. spec)
    def interpret_write(self, instruction: object) -> None:
        if len(instruction.args) != 1:
            Error.handle_error(Error.XML_STRUCT.value)
        value, type = self.get_val_and_type(instruction.args[0])
        value = str(value)
        
        if type == 'nil':
            value = ''

        string = re.sub(b'\\\\(\d{3})', self.replace, value.encode('utf-8'))
        print(string.decode('utf-8'), end='')


    def interpret_concat(self, instruction: object) -> None:
        if len(instruction.args) != 3:
            Error.handle_error(Error.XML_STRUCT.value)
        
        frame, var_name = self.get_var_frame_and_name(instruction.args[0].value)
        value_1, type_1 = self.get_val_and_type(instruction.args[1])
        value_2, type_2 = self.get_val_and_type(instruction.args[2])
        
        if type_1 != 'string' or type_2 != 'string':
            Error.handle_error(Error.OP_TYPES.value)
        value = value_1 + value_2
        self.frames.set_var(var_name, frame, value, 'string')

    def interpret_jump(self, instruction: object) -> None:
        if len(instruction.args) != 1:
            Error.handle_error(Error.XML_STRUCT.value)
        label_name = instruction.args[0].value
        if label_name in self.labels:
            self.position = self.labels.get(label_name)
        else:
            Error.handle_error(Error.SEMANTIC.value)

    # TODO: jeden operand môže byť nil
    def interpret_jumpifeq(self, instruction: object) -> None:
        if len(instruction.args) != 3:
            Error.handle_error(Error.XML_STRUCT.value)
        
        value_1, type_1 = self.get_val_and_type(instruction.args[1])
        value_2, type_2 = self.get_val_and_type(instruction.args[2])

        label_name = instruction.args[0].value
        if label_name in self.labels:
            if type_1 == type_2 and value_1 == value_2:
                self.position = self.labels.get(label_name)
        else:
            Error.handle_error(Error.SEMANTIC.value)

    def interpret_createframe(self, instruction) -> None:
        if len(instruction.args) != 0:
            Error.handle_error(Error.XML_STRUCT.value)
        self.frames.create_frame()

    def interpret_pushframe(self, instruction) -> None:
        if len(instruction.args) != 0:
            Error.handle_error(Error.XML_STRUCT.value)
        self.frames.push_frame()

    def interpret_popframe(self, instruction) -> None:
        if len(instruction.args) != 0:
            Error.handle_error(Error.XML_STRUCT.value)
        self.frames.pop_frame()

    def interpret_add_sub_mul_idiv(self, instruction: object, mode) -> None:
        if len(instruction.args) != 3:
            Error.handle_error(Error.XML_STRUCT.value)
        frame, var_name = self.get_var_frame_and_name(instruction.args[0].value)
        
        value_1, type_1 = self.get_val_and_type(instruction.args[1])
        value_2, type_2 = self.get_val_and_type(instruction.args[2])
        
        if type_1 != 'int' or type_2 != 'int':
            Error.handle_error(Error.OP_TYPES.value)

        match mode:
            case 'add': value = value_1 + value_2
            case 'sub': value = value_1 - value_2
            case 'mul': value = value_1 * value_2
            case 'idiv':
                if value_2 == 0:
                    Error.handle_error(Error.OP_VAL.value)
                else:
                    value = value_1 // value_2
        
        self.frames.set_var(var_name, frame, value, type_1)

    def interpret_exit(self, instruction: object) -> None:
        if len(instruction.args) != 1:
            Error.handle_error(Error.XML_STRUCT.value)
        type = instruction.args[0].type
        value = instruction.args[0].value

        if type != 'int':
            Error.handle_error(Error.OP_TYPES.value)

        if value >= 0 and value <= 49:
            exit(value)
        else:
            Error.handle_error(Error.OP_VAL.value)

    def interpret_type(self, instruction: object) -> None:
        if len(instruction.args) != 2:
            Error.handle_error(Error.XML_STRUCT.value)

        frame_to, var_name_to = self.get_var_frame_and_name(instruction.args[0].value)

        type = instruction.args[1].type
        value = instruction.args[1].value
        if type == 'var':
            frame_from, var_name_from = self.get_var_frame_and_name(value)
            type = self.frames.get_var_type(var_name_from, frame_from)

        self.frames.set_var(var_name_to, frame_to, type, 'string')

    def interpret_read(self, instruction: object) -> None:
        if len(instruction.args) != 2:
            Error.handle_error(Error.XML_STRUCT.value)

        frame, var_name = self.get_var_frame_and_name(instruction.args[0].value)
        input_type = instruction.args[1].value
        
        value = input()
        if self.input == 'STDIN':
            value = input()
        else:
            try:
                f = open(self.input, "r")
            except (FileNotFoundError, PermissionError):
                Error.handle_error(Error.IN_FILE.value)
            value = f.readline()
        
        match input_type:
            case 'int': value = int(value)
            case 'bool': value = Mybool(value)

        self.frames.set_var(var_name, frame, value, input_type)

    def interpret_call(self, instruction: object) -> None:
        pass

    def interpret_return(self, instruction: object) -> None:
        pass

    def interpret_pushs(self, instruction: object) -> None:
        pass

    def interpret_pops(self, instruction: object) -> None:
        pass

    def interpret_ltgteq(self, instruction: object) -> None:
        pass

    def interpret_andornot(self, instruction: object) -> None:
        pass

    def interpret_int2char(self, instruction: object) -> None:
        pass
    
    def interpret_stri2int(self, instruction: object) -> None:
        pass

    def interpret_strlen(self, instruction: object) -> None:
        pass

    def interpret_getchar(self, instruction: object) -> None:
        pass

    def interpret_setchar(self, instruction: object) -> None:
        pass

    def interpret_jumpifneq(self, instruction: object) -> None:
        pass

    def interpret_dprint(self, instruction: object) -> None:
        pass

    def interpret_break(self, instruction: object) -> None:
        pass