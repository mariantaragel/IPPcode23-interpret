## @file program.py
# @brief Program representation
# @author Marián Tarageľ

from error import Error
from frames import Frames
import re
import xml_tree
import interpret_tools as tool
import sys

class Program:

    instructions: list
    position: int
    labels: dict
    frames = Frames()
    input
    call_stack: list
    data_stack: list
    instructions_executed: int
    last_instruction: object

    def __init__(self, input):
        self.instructions = []
        self.position = 0
        self.labels = {}
        self.input = input
        self.call_stack = []
        self.data_stack = []
        self.instructions_executed = 0
        self.last_instruction = None

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
            print(instruction.opcode, instruction.order)
        
            arg1 = None
            arg2 = None
            arg3 = None
            for subchild in child:
                argument = xml_tree.check_element_arg(subchild)
                if argument.position == 0:
                    arg1 = argument
                elif argument.position == 1:
                    arg2 = argument
                else:
                    arg3 = argument

            instruction.add_args(arg1, arg2, arg3)
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

    def interpret_write_dprint(self, instruction: object, stream) -> None:
        value, type = self.get_val_and_type(instruction.args[0])
        value = str(value)
        
        if type == 'nil':
            value = ''
        elif type == 'bool':
            value = value.lower()

        print(value, end='', file=stream)

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
        value, type = self.get_val_and_type(instruction.args[0])

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

    def interpret_read(self, instruction: object) -> None:
        frame, var_name = tool.get_var_frame_and_name(instruction.args[0].value)
        type = instruction.args[1].value
        
        if self.input == 'STDIN':
            value = input()
        else:
            value = self.input.readline()
        
        value = tool.convert(type, value)
        
        if value == None or value == '':
            self.frames.set_var(var_name, frame, 'nil', 'nil')
        else:
            if type == 'string':
                value = value.strip()
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
        value, type = self.get_val_and_type(instruction.args[0])
        self.data_stack.insert(0, (value, type))

    def interpret_pops(self, instruction: object) -> None:
        frame, var_name = tool.get_var_frame_and_name(instruction.args[0].value)
        if self.data_stack != []:
            top_stack_item = self.data_stack.pop(0)
            value = top_stack_item[0]
            type = top_stack_item[1]
        else:
            Error.handle_error(Error.MISSING_VAL.value)

        self.frames.set_var(var_name, frame, value, type)

    def interpret_getchar(self, instruction: object) -> None:
        frame, var_name = tool.get_var_frame_and_name(instruction.args[0].value)
        string, string_type = self.get_val_and_type(instruction.args[1])
        index, index_type = self.get_val_and_type(instruction.args[2])

        if string_type != 'string' or index_type != 'int':
            Error.handle_error(Error.OP_TYPES.value)
        if len(string) <= index or index < 0 or string == '':
            Error.handle_error(Error.STRING.value)

        char = string[index]
        self.frames.set_var(var_name, frame, char, 'string')

    def interpret_int2char(self, instruction: object) -> None:
        frame, var_name = tool.get_var_frame_and_name(instruction.args[0].value)
        number, type = self.get_val_and_type(instruction.args[1])

        if type != 'int':
            Error.handle_error(Error.OP_TYPES.value)

        try:
            char = chr(number)
        except ValueError:
            Error.handle_error(Error.STRING.value)
        self.frames.set_var(var_name, frame, char, 'string')

    def interpret_break(self, instruction: object) -> None:
        print("Last instruction: ", end="")
        if self.last_instruction != None:
            print(self.last_instruction.opcode)
        else:
            print("None")
        print("Code postition: " + str(instruction.order), file=sys.stderr)
        print("Instructions executed: " + str(self.instructions_executed), file=sys.stderr)
        print()
        self.frames.print_frames()
        print()
        print("Data stack:")
        print(self.data_stack)
        print()
        print("Call stack:")
        print(self.call_stack)
