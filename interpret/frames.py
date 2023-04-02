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

    def create_frame(self) -> None:
        self.temporary_frame = {}

    def push_frame(self) -> None:
        if self.temporary_frame != None:
            self.frame_stack.insert(0, self.temporary_frame)
            self.temporary_frame = None
        else:
            Error.handle_error(Error.NO_FRAME.value)

    def pop_frame(self) -> None:
        if self.frame_stack != []:
            top_local_frame = self.frame_stack.pop(0)
            self.temporary_frame = top_local_frame
        else:
            Error.handle_error(Error.NO_FRAME.value)

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

    def def_var(self, var_name: str, frame_name: str) -> None:
        frame = self.get_frame(frame_name)
        if var_name not in frame:
            frame[var_name] = None
        else:
            Error.handle_error(Error.SEMANTIC.value)

    def set_var(self, var_name, frame_name: str, value: str, type: str) -> None:
        frame = self.get_frame(frame_name)
        
        if type == 'var':
            value = value.split("@")
            frame_from = value[0]
            var_name_from = value[1]
            var = self.get_var(var_name_from, frame_from)
            type = var.type
            value = var.value
        
        if var_name in frame:
            new_var = Variable(var_name, value, type)
            frame[var_name] = new_var
        else:
            Error.handle_error(Error.NO_VAR.value)

    def get_var(self, var_name: str, frame_name: str):
        frame = self.get_frame(frame_name)
        if var_name in frame:
            value = frame.get(var_name)
            if value == None:
                Error.handle_error(Error.MISSING_VAL.value)
        else:
            Error.handle_error(Error.NO_VAR.value)
        return value