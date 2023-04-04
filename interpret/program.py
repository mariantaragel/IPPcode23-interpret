## @file program.py
# @brief Program representation
# @author Marián Tarageľ

from error import Error
from frames import Frames
import re
import xml_tree
import interpret_tools as tool

class Program:

    instructions: list
    position: int
    labels: dict
    frames = Frames()
    input
    call_stack: list

    def __init__(self, input):
        self.instructions = []
        self.position = 0
        self.labels = {}
        self.input = input
        self.call_stack = []

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
    
    def get_val_and_type(self, instruction_arg: object) -> tuple:
        value = instruction_arg.value
        type = instruction_arg.type
        if type == 'var':
            frame, var_name = tool.get_var_frame_and_name(instruction_arg.value)
            var = self.frames.get_var(var_name, frame)
            value = var.value
            type = var.type
        elif type == 'string':
            bytes = re.sub(b'\\\\(\d{3})', tool.replace, value.encode('utf-8'))
            value = bytes.decode('utf-8')
        return value, type

    def interpret_defvar(self, instruction: object) -> None:
        frame, var_name = tool.get_var_frame_and_name(instruction.args[0].value)
        self.frames.def_var(var_name, frame)

    def interpret_move(self, instruction: object) -> None:
        frame, var_name = tool.get_var_frame_and_name(instruction.args[0].value)
        value, type = self.get_val_and_type(instruction.args[1])
        self.frames.set_var(var_name, frame, value, type)

    def interpret_write(self, instruction: object) -> None:
        value, type = self.get_val_and_type(instruction.args[0])
        value = str(value)
        
        if type == 'nil':
            value = ''
        elif type == 'bool':
            value = value.lower()

        print(value, end='')

    def interpret_concat(self, instruction: object) -> None:
        frame, var_name = tool.get_var_frame_and_name(instruction.args[0].value)
        value_1, type_1 = self.get_val_and_type(instruction.args[1])
        value_2, type_2 = self.get_val_and_type(instruction.args[2])
        
        if type_1 != 'string' or type_2 != 'string':
            Error.handle_error(Error.OP_TYPES.value)
        value = value_1 + value_2
        self.frames.set_var(var_name, frame, value, 'string')

    def interpret_jump(self, label_name: str) -> None:
        if self.is_label_defined(label_name):
            self.position = self.labels.get(label_name)

    def is_label_defined(self, label_name: str):
        if label_name in self.labels:
            return True
        else:
            Error.handle_error(Error.SEMANTIC.value)

    def interpret_jumpif(self, instruction: object, mode: str) -> None:
        label_name = instruction.args[0].value
        value_1, type_1 = self.get_val_and_type(instruction.args[1])
        value_2, type_2 = self.get_val_and_type(instruction.args[2])
        
        if self.is_label_defined(label_name):
            if type_1 == type_2 or type_1 == 'nil' or type_2 == 'nil':
                match mode:
                    case 'eq':
                        if value_1 == value_2:
                            self.interpret_jump(label_name)
                    case 'neq':
                        if value_1 != value_2:
                            self.interpret_jump(label_name)
            else:
                Error.handle_error(Error.OP_TYPES.value)

    def interpret_call(self, label_name: str) -> None:
        self.call_stack.insert(0, self.position)
        self.interpret_jump(label_name)
        
    def interpret_return(self) -> None:
        if self.call_stack != []:
            return_position = self.call_stack.pop(0)
            self.position = return_position
        else:
            Error.handle_error(Error.MISSING_VAL.value)

    def interpret_createframe(self) -> None:
        self.frames.create_frame()

    def interpret_pushframe(self) -> None:
        self.frames.push_frame()

    def interpret_popframe(self) -> None:
        self.frames.pop_frame()

    def interpret_add_sub_mul_idiv(self, instruction: object, mode) -> None:
        frame, var_name = tool.get_var_frame_and_name(instruction.args[0].value)
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
        type = instruction.args[0].type
        value = instruction.args[0].value

        if type != 'int':
            Error.handle_error(Error.OP_TYPES.value)

        if value >= 0 and value <= 49:
            exit(value)
        else:
            Error.handle_error(Error.OP_VAL.value)

    def interpret_type(self, instruction: object) -> None:
        frame_to, var_name_to = tool.get_var_frame_and_name(instruction.args[0].value)
        type = instruction.args[1].type
        value = instruction.args[1].value

        if type == 'var':
            frame_from, var_name_from = tool.get_var_frame_and_name(value)
            type = self.frames.get_var_type(var_name_from, frame_from)

        self.frames.set_var(var_name_to, frame_to, type, 'string')

    # TODO: zlý vstup -> nil@nil
    def interpret_read(self, instruction: object) -> None:
        frame, var_name = tool.get_var_frame_and_name(instruction.args[0].value)
        type = instruction.args[1].value
        
        if self.input == 'STDIN':
            value = input()
        else:
            value = self.input.readline().strip()

        value = tool.convert(type, value)
        self.frames.set_var(var_name, frame, value, type)

    def interpret_andor(self, instruction: object, mode: str) -> None:
        frame, var_name = tool.get_var_frame_and_name(instruction.args[0].value)
        value_1, type_1 = self.get_val_and_type(instruction.args[1])
        value_2, type_2 = self.get_val_and_type(instruction.args[2])
        
        if type_1 != 'bool' or type_2 != 'bool':
            Error.handle_error(Error.OP_TYPES.value)

        match mode:
            case 'and': value = value_1 and value_2
            case 'or': value = value_1 or value_2

        self.frames.set_var(var_name, frame, value, 'bool')
    
    def interpret_not(self, instruction: object) -> None:
        frame, var_name = tool.get_var_frame_and_name(instruction.args[0].value)
        
        value, type = self.get_val_and_type(instruction.args[1])
        
        if type != 'bool':
            Error.handle_error(Error.OP_TYPES.value)

        value = not value
        self.frames.set_var(var_name, frame, value, 'bool')

    def interpret_ltgteq(self, instruction: object, mode: str) -> None:
        frame, var_name = tool.get_var_frame_and_name(instruction.args[0].value)
        value_1, type_1 = self.get_val_and_type(instruction.args[1])
        value_2, type_2 = self.get_val_and_type(instruction.args[2])
        
        if type_1 == 'nil' or type_2 == 'nil':
            if mode != 'eq':
                Error.handle_error(Error.OP_TYPES.value)
        elif type_1 != type_2:
            Error.handle_error(Error.OP_TYPES.value)

        match mode:
            case 'lt': value = value_1 < value_2
            case 'gt': value = value_1 > value_2
            case 'eq': value = value_1 == value_2
        
        self.frames.set_var(var_name, frame, value, 'bool')

    def interpret_setchar(self, instruction: object) -> None:
        frame, var_name = tool.get_var_frame_and_name(instruction.args[0].value)
        string, string_type = self.get_val_and_type(instruction.args[0])
        index, index_type = self.get_val_and_type(instruction.args[1])
        char, char_type = self.get_val_and_type(instruction.args[2])

        if string_type != 'string' or index_type != 'int' or char_type != 'string':
            Error.handle_error(Error.OP_TYPES.value)
        if len(string) <= index or index < 0 or char == '':
            Error.handle_error(Error.STRING.value)


        string = string[:index] + char[0] + string[index + 1:]
        self.frames.set_var(var_name, frame, string, 'string')

    def interpret_strlen(self, instruction: object) -> None:
        frame, var_name = tool.get_var_frame_and_name(instruction.args[0].value)
        string, type = self.get_val_and_type(instruction.args[1])
        
        if type != 'string':
            Error.handle_error(Error.OP_TYPES.value)

        strlen = len(string)
        self.frames.set_var(var_name, frame, strlen, 'int')

    def interpret_stri2int(self, instruction: object) -> None:
        frame, var_name = tool.get_var_frame_and_name(instruction.args[0].value)
        string, string_type = self.get_val_and_type(instruction.args[1])
        index, index_type = self.get_val_and_type(instruction.args[2])

        if string_type != 'string' or index_type != 'int':
            Error.handle_error(Error.OP_TYPES.value)
        if len(string) <= index or index < 0 or string == '':
            Error.handle_error(Error.STRING.value)

        ord_val = ord(string[index])
        self.frames.set_var(var_name, frame, ord_val, 'int')        

    def interpret_pushs(self, instruction: object) -> None:
        pass

    def interpret_pops(self, instruction: object) -> None:
        pass

    def interpret_int2char(self, instruction: object) -> None:
        pass

    def interpret_getchar(self, instruction: object) -> None:
        pass

    def interpret_dprint(self, instruction: object) -> None:
        pass

    def interpret_break(self, instruction: object) -> None:
        pass