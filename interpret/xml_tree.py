## @file xml_tree.py
# @brief XML tree check functions
# @author Marián Tarageľ

from error import Error
import re

def check_program_element(program: object) -> None:
    if (program.tag != 'program' or
        program.attrib.get('language') != 'IPPcode23'):
        
        Error.handle_error(Error.XML_STRUCT.value)

def check_instruction_elements(program: object) -> None:
    for instruction in program:
        check_element_instruction(instruction)
        for arg in instruction:
            check_element_arg(arg)

def check_element_instruction(instruction: object) -> None:
    opcode = instruction.attrib.get('opcode')
    order = instruction.attrib.get('order')
    if opcode not in ['MOVE', 'CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'DEFVAR',
                      'CALL', 'RETURN', 'PUSHS', 'POPS', 'ADD', 'SUB', 'MUL',
                      'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR', 'NOT', 'INT2CHAR'
                      'STRI2INT', 'READ', 'WRITE', 'CONCAT', 'STRLEN',
                      'GETCHAR', 'SETCHAR', 'TYPE', 'LABEL', 'JUMP', 'JUMPIFEQ',
                      'JUMPIFNEQ', 'EXIT', 'DPRINT', 'BREAK']:
        Error.handle_error(Error.XML_STRUCT.value)

    if (instruction.tag != 'instruction' or order == None or
        re.match('^[1-9]\d*$', str(order)) == None):

        Error.handle_error(Error.XML_STRUCT.value)

def check_element_arg(arg: object) -> None:
    if (re.match('arg[123]', arg.tag) == None or
        arg.attrib.get('type') == None):
        
        Error.handle_error(Error.XML_STRUCT.value)