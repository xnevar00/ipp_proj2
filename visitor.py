import sys
import abc
from operations import *

class Visitor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def visit_DEFVAR(self, element : DEFVAR, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_MOVE(self, element : MOVE, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_WRITE(self, element : WRITE, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_CREATEFRAME(self, element : CREATEFRAME, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_PUSHFRAME(self, element : PUSHFRAME, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_POPFRAME(self, element : POPFRAME, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_ADD_SUB_MUL_IDIV(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_LT_GT_EQ(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_LT_GT_EQ(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_LT_GT_EQ(self, element, instruction, interpret):
        pass


class Interpreter(Visitor):
    def visit_DEFVAR(self, element : DEFVAR, instruction, interpret):
        frame, name = parseFrameAndName(instruction.find('arg1').text)
        if (checkExistingFrame(frame, interpret) == True):
            if (checkExistingVar(frame, name, interpret) == False):
                match frame:
                    case "GF":
                        interpret.frames["GF"][name] = {"value" : None, "type" : UNDEFINEDTYPE}
                    case "LF":
                        interpret.frames["LF"][name] = {"value" : None, "type" : UNDEFINEDTYPE}
                    case "TF":
                        interpret.frames["TF"][name] = {"value" : None, "type" : UNDEFINEDTYPE}
            else:
                print("Pokus o definovani jiz existujici promenne", file=sys.stderr)
                exit(52)
        else:
            print("Nelze definovat promennou v neexistujicim ramci", file=sys.stderr)
            exit(55)

    def visit_MOVE(self, element : MOVE, instruction, interpret):
        destination = instruction.find('arg1').text
        frame, name = parseFrameAndName(instruction.find('arg1').text)

        type = instruction.find('arg2').attrib['type']
        value = instruction.find('arg2').text
        type_of_var = Type.UNDEFINED
        match type:
            case "int":
                value = int(instruction.find('arg2').text)
                type_of_var = Type.INT
            case "string":
                value = instruction.find('arg2').text
                type_of_var = Type.STRING
            case "nil":
                value = None
                type_of_var = Type.NIL
            case "bool":
                value = instruction.find('arg2').text
                type_of_var = Type.BOOL
            case _:
                srcframe, srcname = parseFrameAndName(instruction.find('arg2').text)
                value = interpret.frames[srcframe][srcname]["value"]
                type_of_var = interpret.frames[srcframe][srcname]["type"]
        interpret.frames[frame][name]["value"] = value
        interpret.frames[frame][name]["type"] = type_of_var
    
    def visit_WRITE(self, element : WRITE, instruction, interpret):
        value = handleArgument(instruction, interpret)
        print(value, end='')
    
    def visit_CREATEFRAME(self, element : CREATEFRAME, instruction, interpret):
        interpret.frames["TF"] = {}

    def visit_PUSHFRAME(self, element : PUSHFRAME, instruction, interpret):
        interpret.LFstack.append(interpret.frames["LF"])
        interpret.frames["LF"] = interpret.frames["TF"]
        interpret.frames["TF"] = UNDEFINEDSTACK

    def visit_POPFRAME(self, element : POPFRAME, instruction, interpret):
        if (checkExistingFrame("LF", interpret) == True):
            interpret.frames["TF"] = interpret.frames["LF"]
            if (len(interpret.LFstack) != 0):
                interpret.frames["LF"] = interpret.LFstack.pop()
            else:
                interpret.frames["LF"] = UNDEFINEDSTACK
        else:
            print("Zasobnik lokalnich ramcu je prazdny, POPFRAME nelze provest", file=sys.stderr)
            exit(55)

    def visit_ADD_SUB_MUL_IDIV(self, element, instruction, interpret, operation):
        arg2 = instruction.find('arg2')
        arg3 = instruction.find('arg3')
        type_arg2, value_arg2 = checkSymbTypeAndValue(arg2, interpret)
        type_arg3, value_arg3 = checkSymbTypeAndValue(arg3, interpret)
        if ((type_arg2 == Type.INT) and (type_arg3 == Type.INT)):
            frame, name = parseFrameAndName(instruction.find('arg1').text)
            if (checkExistingFrame(frame, interpret) == False):
                print("Dany ramec neexistuje", file=sys.stderr)
                exit(55)
            if (checkExistingVar(frame, name, interpret) == False):
                print("Dana promenna neexistuje", file=sys.stderr)
                exit(54)
            #TODO: udelat podporu edgecasu, napr int@+12
            match operation:
                case "ADD":
                    interpret.frames[frame][name]["value"] = int(value_arg2) + int(value_arg3)
                case "SUB":
                    interpret.frames[frame][name]["value"] = int(value_arg2) - int(value_arg3)
                case "MUL":
                    interpret.frames[frame][name]["value"] = int(value_arg2) * int(value_arg3)
                case "IDIV":
                    if (int(value_arg3) == 0):
                        print("Deleni nulou", file=sys.stderr)
                        exit(57)
                    interpret.frames[frame][name]["value"] = int(value_arg2) // int(value_arg3)

            interpret.frames[frame][name]["type"] = Type.INT

    def visit_LT_GT_EQ(self, element: LT, instruction, interpret, operation):
        arg1 = instruction.find('arg1')
        arg2 = instruction.find('arg2')
        arg3 = instruction.find('arg3')
        frame_arg1, name_arg1 = parseFrameAndName(arg1.text)

        if (checkExistingFrame(frame_arg1, interpret) == False):
            print("Pristup do nedefinovaneho ramce", file=sys.stderr)
            exit(55)
        elif (checkExistingVar(frame_arg1, name_arg1, interpret) == False):
            print("Promenna neexistuje", file=sys.stderr)
            exit(54)
        else:
            type_arg2, value_arg2 = checkSymbTypeAndValue(arg2, interpret)
            type_arg3, value_arg3 = checkSymbTypeAndValue(arg3, interpret)
            if ((type_arg2 == type_arg3) & (type_arg2 != False) & (type_arg3 != False)):
                match operation:
                    case "LT":
                        if (value_arg2 < value_arg3):
                            interpret.frames[frame_arg1][name_arg1]["value"] = "true"
                        else:
                            interpret.frames[frame_arg1][name_arg1]["value"] = "false"
                    case "GT":
                        if (value_arg2 > value_arg3):
                            interpret.frames[frame_arg1][name_arg1]["value"] = "true"
                        else:
                            interpret.frames[frame_arg1][name_arg1]["value"] = "false"
                    case "EQ":
                        if (value_arg2 == value_arg3):
                            interpret.frames[frame_arg1][name_arg1]["value"] = "true"
                        else:
                            interpret.frames[frame_arg1][name_arg1]["value"] = "false"

                interpret.frames[frame_arg1][name_arg1]["type"] = Type.BOOL
            else:
                print("Nekompatibilni typy v porovnani", file=sys.stderr)
                exit(53)


