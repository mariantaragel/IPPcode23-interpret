## @file my_arg_parse.py
# @brief Argument parser
# @author Marián Tarageľ

import argparse
import sys
from error import Error

class Myargparse(argparse.ArgumentParser):

    @staticmethod
    def is_input_defined(args: object) -> bool:
        if args.source != 'STDIN' or args.input != 'STDIN':
            return True
        else:
            return False

    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        args = {'prog': self.prog, 'message': message}
        self.exit(Error.ARGS.value, ('%(prog)s: error: %(message)s\n') % args)
        
    # Check --help with other arguments
    def check_args_cobination(self, args: object):
        if args.help and self.is_input_defined(args):
            self.error('cannot combine --help with other arguments')
        
    def if_defined_print_help(self, args: object) -> None:
        if args.help:
            self.print_help()
            exit(0)

    def check_no_arguments(self, args: object) -> None:
        if not self.is_input_defined(args):
            self.error('no arguments')