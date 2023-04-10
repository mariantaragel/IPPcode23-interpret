## @file interpret.py
# @brief IPPcode23 interpret
# @author Marián Tarageľ

from argparse import RawDescriptionHelpFormatter
from my_arg_parse import Myargparse
from error import Error
import xml.etree.ElementTree as ET
from program import Program
import sys

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
    if args.input != 'STDIN':
        input_file = open(args.input, "r")
    else:
        input_file = args.input
    if args.source != 'STDIN':
        tree = ET.parse(args.source)
    else:
        tree = ET.parse(sys.stdin)
except (FileNotFoundError, PermissionError):
    Error.handle_error(Error.IN_FILE.value)
except ET.ParseError:
    Error.handle_error(Error.XML_FORMAT.value)

tree = tree.getroot()

program = Program(input_file)
program.get_program_from_xml(tree)
program.prepocessing()

program.position = 0
while True:
    ins_element = program.get_instruction()
    if ins_element == None:
        break
    program.position += 1
    match ins_element.opcode:
        case 'MOVE': program.interpret_move(ins_element)
        case 'CREATEFRAME': program.interpret_createframe()
        case 'PUSHFRAME': program.interpret_pushframe()
        case 'POPFRAME': program.interpret_popframe()
        case 'DEFVAR': program.interpret_defvar(ins_element)
        case 'CALL': program.interpret_call(ins_element.args[0].value)
        case 'RETURN': program.interpret_return()
        case 'PUSHS': program.interpret_pushs(ins_element)
        case 'POPS': program.interpret_pops(ins_element)
        case 'ADD': program.interpret_add_sub_mul_idiv(ins_element, 'add')
        case 'SUB': program.interpret_add_sub_mul_idiv(ins_element, 'sub')
        case 'MUL': program.interpret_add_sub_mul_idiv(ins_element, 'mul')
        case 'IDIV': program.interpret_add_sub_mul_idiv(ins_element, 'idiv')
        case 'LT': program.interpret_ltgteq(ins_element, 'lt')
        case 'GT': program.interpret_ltgteq(ins_element, 'gt')
        case 'EQ': program.interpret_ltgteq(ins_element, 'eq')
        case 'AND': program.interpret_andor(ins_element, 'and')
        case 'OR': program.interpret_andor(ins_element, 'or')
        case 'NOT': program.interpret_not(ins_element)
        case 'INT2CHAR': program.interpret_int2char(ins_element)
        case 'STRI2INT': program.interpret_stri2int(ins_element)
        case 'READ': program.interpret_read(ins_element)
        case 'WRITE': program.interpret_write_dprint(ins_element, sys.stdout)
        case 'CONCAT': program.interpret_concat(ins_element)
        case 'STRLEN': program.interpret_strlen(ins_element)
        case 'GETCHAR': program.interpret_getchar(ins_element)
        case 'SETCHAR': program.interpret_setchar(ins_element)
        case 'TYPE': program.interpret_type(ins_element)
        case 'LABEL': continue
        case 'JUMP': program.interpret_jump(ins_element.args[0].value)
        case 'JUMPIFEQ': program.interpret_jumpif(ins_element, 'eq')
        case 'JUMPIFNEQ': program.interpret_jumpif(ins_element, 'neq')
        case 'EXIT': program.interpret_exit(ins_element)
        case 'DPRINT': program.interpret_write_dprint(ins_element, sys.stderr)
        case 'BREAK': program.interpret_break(ins_element)
        case _: Error.handle_error(Error.XML_STRUCT.value)
    program.instructions_executed += 1
    program.last_instruction = ins_element