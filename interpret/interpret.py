## @file interpret.py
# @brief IPPcode23 interpret
# @author Marián Tarageľ

from argparse import RawDescriptionHelpFormatter
from my_arg_parse import Myargparse
from error import Error
import xml.etree.ElementTree as ET
import xml_tree
from program import Program

parser = Myargparse(formatter_class=RawDescriptionHelpFormatter, description="""
Skript načíta XML reprezentáciu programu a tento program s využitím vstupu
podľa parametrov príkazového riadku interpretuje a generuje výstup.""", add_help=False)
parser.add_argument('--source', metavar='FILE', dest='source', default='STDIN',
help="vstupný súbor s XML reprezentaciou zdrojového kódu")
parser.add_argument('--input', metavar='FILE', dest='input', default='STDIN',
help="soubor se vstupmi pre samotnú interpretáciu zadaného zdrojového kódu")
parser.add_argument('-h', '--help', action='store_true', help='show this help message and exit')

args = parser.parse_args()
parser.check_args_cobination(args)
parser.if_defined_print_help(args)
parser.check_no_arguments(args)

try:
    tree = ET.parse(args.source)
except (FileNotFoundError, PermissionError):
    Error.handle_error(Error.IN_FILE.value)
except ET.ParseError:
    Error.handle_error(Error.XML_FORMAT.value)

tree = tree.getroot()
xml_tree.check_program_element(tree)
xml_tree.check_instruction_elements(tree)

program = Program()
program.get_program_from_xml(tree)
program.prepocessing()

program.position = 0
while True:
    instruction = program.get_instruction()
    if instruction == None:
        break
    program.position += 1
    match instruction.opcode:
        case 'MOVE': program.interpret_move(instruction)
        case 'CREATEFRAME': program.interpret_createframe(instruction)
        case 'PUSHFRAME': program.interpret_pushframe(instruction)
        case 'POPFRAME': program.interpret_popframe(instruction)
        case 'DEFVAR': program.interpret_defvar(instruction)
        case 'CALL': program.interpret_call(instruction)
        case 'RETURN': program.interpret_return(instruction)
        case 'PUSHS': program.interpret_pushs(instruction)
        case 'POPS': program.interpret_pops(instruction)
        case 'ADD': program.interpret_add_sub_mul_idiv(instruction, 'add')
        case 'SUB': program.interpret_add_sub_mul_idiv(instruction, 'sub')
        case 'MUL': program.interpret_add_sub_mul_idiv(instruction, 'mul')
        case 'IDIV': program.interpret_add_sub_mul_idiv(instruction, 'idiv')
        case 'LT' | 'GT' | 'EQ': program.interpret_ltgteq(instruction)
        case 'AND' | 'OR' | 'NOT': program.interpret_andornot(instruction)
        case 'INT2CHAR': program.interpret_int2char(instruction)
        case 'STRI2INT': program.interpret_stri2int(instruction)
        case 'READ': program.interpret_read(instruction)
        case 'WRITE': program.interpret_write(instruction)
        case 'CONCAT': program.interpret_concat(instruction)
        case 'STRLEN': program.interpret_strlen(instruction)
        case 'GETCHAR': program.interpret_getchar(instruction)
        case 'SETCHAR': program.interpret_setchar(instruction)
        case 'TYPE': program.interpret_type(instruction)
        case 'LABEL': continue
        case 'JUMP': program.interpret_jump(instruction)
        case 'JUMPIFEQ': program.interpret_jumpifeq(instruction)
        case 'JUMPIFNEQ': program.interpret_jumpifneq(instruction)
        case 'EXIT': program.interpret_exit(instruction)
        case 'DPRINT': program.interpret_dprint(instruction)
        case 'BREAK': program.interpret_break(instruction)
        case _: Error.handle_error(Error.XML_STRUCT.value)