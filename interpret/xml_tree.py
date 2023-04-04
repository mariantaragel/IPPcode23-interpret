## @file xml_tree.py
# @brief XML tree check functions
# @author Marián Tarageľ

from error import Error
import re
from instruction import Instruction
from argument import Argument
from my_bool import Mybool

def check_program_element(program: object) -> None:
    if (program.tag != 'program' or
        program.attrib.get('language') != 'IPPcode23'):
        
        Error.handle_error(Error.XML_STRUCT.value)

def check_element_instruction(ins: object):
    opcode = ins.attrib.get('opcode')
    order = ins.attrib.get('order')

    if (ins.tag != 'instruction' or
        order == None or opcode == None or
        re.match('^[1-9]\d*$', str(order)) == None):

        Error.handle_error(Error.XML_STRUCT.value)
    
    opcode = opcode.upper()
    if opcode not in ['MOVE', 'CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'DEFVAR',
                      'CALL', 'RETURN', 'PUSHS', 'POPS', 'ADD', 'SUB', 'MUL',
                      'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR', 'NOT', 'INT2CHAR'
                      'STRI2INT', 'READ', 'WRITE', 'CONCAT', 'STRLEN',
                      'GETCHAR', 'SETCHAR', 'TYPE', 'LABEL', 'JUMP', 'JUMPIFEQ',
                      'JUMPIFNEQ', 'EXIT', 'DPRINT', 'BREAK']:
        Error.handle_error(Error.XML_STRUCT.value)

    instruction = Instruction(opcode, int(order))
    return instruction

def check_element_arg(arg: object):
    type = arg.attrib.get('type')
    value = arg.text
    
    if type not in ['int', 'bool', 'string', 'nil', 'label', 'type', 'var']:
        Error.handle_error(Error.XML_STRUCT.value)
    if re.match('arg[123]', arg.tag) == None: 
        Error.handle_error(Error.XML_STRUCT.value)
    
    if value == None:
        value = ""

    match type:
        case 'int':
            try:
                value = int(value)
            except ValueError:
                Error.handle_error(Error.XML_STRUCT.value)
        case 'bool': 
            value = Mybool(value)

    argument = Argument(type, value)
    argument.add_argument_position(arg.tag)
    return argument