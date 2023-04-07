import sys
import abc

UNDEFINEDSTACK = -1

class Operation(metaclass=abc.ABCMeta):
    

    @abc.abstractmethod
    def accept(self, visitor, instruction, interpret):
        pass

    def checkExistingVar(self, frame, var, interpret):
        if var in interpret.frames[frame]:
            return True
        else:
            return False
    
    def checkExistingFrame(self, frame, interpret):
        if (interpret.frames[frame] == UNDEFINEDSTACK):
            return False
        else:
            return True



class DEFVAR(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_DEFVAR(self, instruction, interpret)

class MOVE(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_MOVE(self, instruction, interpret)

class WRITE(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_WRITE(self, instruction, interpret)

    def handleArgument(self, instruction, interpret):
        type = instruction.find('arg1').attrib['type']
        value = instruction.find('arg1').text
        match type:
            case "var":
                var_name_parts = value.split('@')
                frame = var_name_parts[0]
                value = var_name_parts[1]
                if (self.checkExistingFrame(frame, interpret) == False):
                    print("Dany ramec neexistuje", file=sys.stderr)
                    exit(55)
                if (self.checkExistingVar(frame, value, interpret) == True):
                    match frame:
                        case "GF":
                            value = interpret.frames["GF"][value]
                        case "LF":
                            value = interpret.frames["LF"][value]
                        case "TF":
                            value = interpret.frames["TF"][value]
                else:
                    print("Dana promenna neexistuje", file=sys.stderr)
                    exit(54)
            case "nil":
                value = ""
            case "string" | "bool" | "int":
                value = value
        return value

class CREATEFRAME(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_CREATEFRAME(self, instruction, interpret)

class PUSHFRAME(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_PUSHFRAME(self, instruction, interpret)

class POPFRAME(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_POPFRAME(self, instruction, interpret)
