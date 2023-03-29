## @file my_arg_parse.py
# @brief Argument parser
# @author Marián Tarageľ

import argparse
import sys
from error import ERR_ARGS

class Myargparse(argparse.ArgumentParser):

    def error(self, message):
        self.print_usage(sys.stderr)
        args = {'prog': self.prog, 'message': message}
        self.exit(ERR_ARGS, ('%(prog)s: error: %(message)s\n') % args)

    @staticmethod
    def is_input_defined(args) -> bool:
        if args.source != 'STDIN' or args.input != 'STDIN':
            return True
        else:
            return False
        
    def check_args_cobination(self, args):
        if args.help and self.is_input_defined(args):
            self.error('cannot combine --help with other arguments')
        
    def if_defined_print_help(self, args):
        if args.help:
            self.print_help()
            exit(0)

    def check_no_arguments(self, args):
        if not self.is_input_defined(args):
            self.error('no arguments')