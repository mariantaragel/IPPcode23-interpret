## @file interpret.py
# @brief IPPcode23 interpreter
# @author Marián Tarageľ
# @date 23.2.2023

import argparse
import sys
class Myargparse(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        args = {'prog': self.prog, 'message': message}
        self.exit(10, ('%(prog)s: error: %(message)s\n') % args)

def handle_error(error_code):
    print('Error: ' + str(error_code))
    exit(error_code)

parser = Myargparse(formatter_class=argparse.RawDescriptionHelpFormatter, description="""
Skript načíta XML reprezentáciu programu a tento program s využitím vstupu
podľa parametrov príkazového riadku interpretuje a generuje výstup.""")
parser.add_argument('--source', metavar='FILE', dest='source', default='STDIN',
help="vstupný súbor s XML reprezentaciou zdrojového kódu")
parser.add_argument('--input', metavar='FILE', dest='input', default='STDIN',
help="soubor se vstupmi pre samotnú interpretáciu zadaného zdrojového kódu")

args = parser.parse_args()
if args.source == 'STDIN' and args.input == 'STDIN':
    parser.error('no arguments')

print(args.source)
print(args.input)