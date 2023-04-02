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
program.sort_instructions()

for i in program.instructions:
    match i.opcode:
        case 'MOVE': program.interpret_move(i)
        case 'CREATEFRAME': print('CREATEFRAME')
        case 'PUSHFRAME': print('PUSHFRAME')
        case 'POPFRAME': print('POPFRAME')
        case 'DEFVAR': program.interpret_defvar(i)
        case 'CALL': print('CALL')
        case 'RETURN': print('RETURN')
        case 'PUSHS': print('PUSHS')
        case 'POPS': print('POPS')
        case 'ADD': print('ADD')
        case 'SUB': print('SUB')
        case 'MUL': print('MUL')
        case 'IDIV': print('IDIV')
        case 'LT' | 'GT' | 'EQ': print('LT/GT/EQ')
        case 'AND' | 'OR' | 'NOT': print('AND/OR/NOT')
        case 'INT2CHAR': print('AND')
        case 'STRI2INT': print('RETURN')
        case 'READ': print('READ')
        case 'WRITE': program.interpret_write(i)
        case 'CONCAT': continue
        case 'STRLEN': print('STRLEN')
        case 'GETCHAR': print('GETCHAR')
        case 'SETCHAR': print('SETCHAR')
        case 'TYPE': print('TYPE')
        case 'LABEL': continue
        case 'JUMP': continue
        case 'JUMPIFEQ': continue
        case 'JUMPIFNEQ': print('JUMPIFNEQ')
        case 'EXIT': print('EXIT')
        case 'DPRINT': print('DPRINT')
        case 'BREAK': print('BREAK')