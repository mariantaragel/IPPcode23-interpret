## @file interpret.py
# @brief IPPcode23 interpret
# @author Marián Tarageľ

from argparse import RawDescriptionHelpFormatter
from my_arg_parse import Myargparse
import xml.etree.ElementTree as ET
from error import *
import re

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
    Error.handle_error(ERR_IN_FILE)
except ET.ParseError:
    Error.handle_error(ERR_XML_FORMAT)


root = tree.getroot()

if root.tag != 'program':
    Error.handle_error(ERR_XML_STRUCT)

if root.attrib.get('language') != 'IPPcode23':
    Error.handle_error(ERR_XML_STRUCT)

for child in root:
    if child.tag != 'instruction':
        Error.handle_error(ERR_XML_STRUCT)
    if child.attrib.get('order') == None:
        Error.handle_error(ERR_XML_STRUCT)
    if child.attrib.get('opcode') == None:
        Error.handle_error(ERR_XML_STRUCT)
    if re.match('^\d*$', child.attrib.get('order')) == None:
        Error.handle_error(ERR_XML_STRUCT)
    