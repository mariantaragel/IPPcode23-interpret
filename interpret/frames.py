## @file frames.py
# @brief Frames representation
# @author Marián Tarageľ

from error import Error
from variable import Variable

class Frames:

    global_frame: dict
    temporary_frame: dict
    frame_stack: list

    def __init__(self):
        self.global_frame = {}
        self.temporary_frame = None
        self.frame_stack = []

    # New TF
    def create_frame(self) -> None:
        self.temporary_frame = {}

    # New LF
    def push_frame(self) -> None:
        if self.temporary_frame != None:
            self.frame_stack.insert(0, self.temporary_frame)
            self.temporary_frame = None
        else:
            Error.handle_error(Error.NO_FRAME.value)

    # Move LF to TF
    def pop_frame(self) -> None:
        if self.frame_stack != []:
            top_local_frame = self.frame_stack.pop(0)
            self.temporary_frame = top_local_frame
        else:
            Error.handle_error(Error.NO_FRAME.value)

    # Return instance of frame
    def get_frame(self, frame):
        match frame:
            case 'GF':
                return self.global_frame
            case 'TF':
                if self.temporary_frame != None:
                    return self.temporary_frame
                else:
                    Error.handle_error(Error.NO_FRAME.value)
            case 'LF':
                if len(self.frame_stack) > 0:
                    return self.frame_stack[0]
                else:
                    Error.handle_error(Error.NO_FRAME.value)
            case _:
                Error.handle_error(Error.SEMANTIC.value)

    # New variable
    def def_var(self, var_name: str, frame_name: str) -> None:
        frame = self.get_frame(frame_name)
        if var_name not in frame:
            frame[var_name] = None
        else:
            Error.handle_error(Error.SEMANTIC.value)

    # Set variable value
    def set_var(self, var_name, frame_name: str, value, type: str) -> None:
        frame = self.get_frame(frame_name)
        if var_name in frame:
            new_var = Variable(var_name, value, type)
            frame[var_name] = new_var
        else:
            Error.handle_error(Error.NO_VAR.value)

    # Get variable value
    def get_var(self, var_name: str, frame_name: str):
        frame = self.get_frame(frame_name)
        if var_name in frame:
            var = frame.get(var_name)
            if var == None:
                Error.handle_error(Error.MISSING_VAL.value)
        else:
            Error.handle_error(Error.NO_VAR.value)
        return var
    
    # Get variable type
    def get_var_type(self, var_name: str, frame_name: str):
        frame = self.get_frame(frame_name)
        if var_name in frame:
            var = frame.get(var_name)
            if var == None:
                return ''
            else:
                return var.type
        else:
            Error.handle_error(Error.NO_VAR.value)

    # Print current state of all frames (GF, LF, TF)
    def print_frames(self) -> None:
        print("Global frame:")
        self.print_frame(self.global_frame)
        print()

        print("Local frame:")
        if len(self.frame_stack) == 0:
            print("Undefined")
        else:
            self.print_frame(self.frame_stack[0])
        print()

        print("Temporary frame:")
        if self.temporary_frame == None:
            print("Undefined")
        else:
            self.print_frame(self.temporary_frame)

    # Print one frame state
    @staticmethod
    def print_frame(frame: dict) -> None:
        print("{", end="")
        first = True
        for var_name in frame:
            if not first:
                print(", ", end="")
            var = frame.get(var_name)
            print("'" + var_name + "': ", end="")
            if var != None:
                print("'" + str(var.value) + "'", end="")
            else:
                print("None", end="")
            first = False
        print("}")