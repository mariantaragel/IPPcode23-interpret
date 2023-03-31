## @file interpret.py
# @brief IPPcode23 interpret
# @author Marián Tarageľ

from argparse import RawDescriptionHelpFormatter
from my_arg_parse import Myargparse
from error import Error
import xml.etree.ElementTree as ET
import xml_tree
from instruction import Instruction
from argument import Argument

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

program = tree.getroot()
xml_tree.check_program_element(program)
xml_tree.check_instruction_elements(program)

for instruction in program:
    opcode = instruction.attrib.get('opcode').upper()
    order = instruction.attrib.get('order')
    ins = Instruction(opcode, order)
    
    for argument in instruction:
        type = argument.attrib.get('type')
        value = argument.text
        arg = Argument(type, value)
        ins.add_arg(arg)