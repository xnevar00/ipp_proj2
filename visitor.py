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

class Interpreter(Visitor):
    def visit_DEFVAR(self, element : DEFVAR, instruction, interpret):
        var = instruction.find('arg1').text
        var_name_parts = var.split('@')
        frame = var_name_parts[0]
        name = var_name_parts[1]
        if (element.checkExistingFrame(frame, interpret) == True):
            if (element.checkExistingVar(frame, name, interpret) == False):
                match frame:
                    case "GF":
                        interpret.frames["GF"][name] = UNDEFINEDSTACK
                    case "LF":
                        interpret.frames["LF"][name] = UNDEFINEDSTACK
                    case "TF":
                        interpret.frames["TF"][name] = UNDEFINEDSTACK
            else:
                print("Pokus o definovani jiz existujici promenne", file=sys.stderr)
                exit(52)
        else:
            print("Nelze definovat promennou v neexistujicim ramci", file=sys.stderr)
            exit(55)

    def visit_MOVE(self, element : MOVE, instruction, interpret):
        destination = instruction.find('arg1').text
        var_name_parts = destination.split('@')
        frame = var_name_parts[0]
        name = var_name_parts[1]

        type = instruction.find('arg2').attrib['type']
        value = instruction.find('arg2').text
        match type:
            case "int":
                value = int(instruction.find('arg2').text)
            case "string":
                value = instruction.find('arg2').text
            case "nil":
                value = None
            case _:
                var_name_parts = instruction.find('arg2').text.split('@')
                srcframe = var_name_parts[0]
                srcname = var_name_parts[1]
                value = interpret.frames[srcframe][srcname]
        interpret.frames[frame][name] = value
    
    def visit_WRITE(self, element : WRITE, instruction, interpret):
        value = element.handleArgument(instruction, interpret)
        print(value, end='')
    
    def visit_CREATEFRAME(self, element : CREATEFRAME, instruction, interpret):
        interpret.frames["TF"] = {}

    def visit_PUSHFRAME(self, element : PUSHFRAME, instruction, interpret):
        interpret.LFstack.append(interpret.frames["LF"])
        interpret.frames["LF"] = interpret.frames["TF"]
        interpret.frames["TF"] = UNDEFINEDSTACK

    def visit_POPFRAME(self, element : POPFRAME, instruction, interpret):
        if (element.checkExistingFrame("LF", interpret) == True):
            interpret.frames["TF"] = interpret.frames["LF"]
            if (len(interpret.LFstack) != 0):
                interpret.frames["LF"] = interpret.LFstack.pop()
            else:
                interpret.frames["LF"] = UNDEFINEDSTACK
        else:
            print("Zasobnik lokalnich ramcu je prazdny, POPFRAME nelze provest", file=sys.stderr)
            exit(55)
