#           IPP projekt 2
#
# author:   Veronika Nevarilova (xnevar00)
# date:     4/2022
# file:     visitor.py

import sys
import abc
from operations import *
import re

class Visitor(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def visit_DEFVAR(self, element : DEFVAR, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_MOVE(self, element : MOVE, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_WRITE_DPRINT(self, element : WRITE, instruction, interpret):
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
    def visit_LT_GT_EQ_AND_OR(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_NOT(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_INT2CHAR(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_STRI2INT(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_CONCAT(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_STRLEN(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_GETCHAR(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_SETCHAR(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_EXIT(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_TYPE(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_PUSHS(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_POPS(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_BREAK(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_LABEL(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_JUMP(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_JUMPIFEQ_JUMPIFNEQ(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_CALL(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_RETURN(self, element, instruction, interpret):
        pass

    @abc.abstractmethod
    def visit_READ(self, element, instruction, interpret):
        pass

class Interpreter(Visitor):
    def __init__(self):
        self.op_counter = 0         # increments with every operation done, or changes when jumping to labels
        self.total_exec_op_cnt = 0  # for debug print, only increments

    def visit_DEFVAR(self, element : DEFVAR, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

        frame, name = parseFrameAndName(instruction.find('arg1').text)
        if (checkExistingFrame(frame, interpret) == True):
            if (checkExistingVar(frame, name, interpret) == False):
                match frame:
                    case "GF":
                        interpret.frames["GF"][name] = {"value" : None, "type" : Type.UNDEFINED}
                    case "LF":
                        interpret.frames["LF"][name] = {"value" : None, "type" : Type.UNDEFINED}
                    case "TF":
                        interpret.frames["TF"][name] = {"value" : None, "type" : Type.UNDEFINED}
            else:
                print("Pokus o definovani jiz existujici promenne", file=sys.stderr)
                exit(52)
        else:
            print("Nelze definovat promennou v neexistujicim ramci", file=sys.stderr)
            exit(55)

    def visit_MOVE(self, element : MOVE, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

        frame, name = parseFrameAndName(instruction.find('arg1').text)
        if (checkExistingFrame(frame, interpret) == False):
            print("Ramec neexistuje", file=sys.stderr)
            exit(55)
        if (checkExistingVar(frame, name, interpret) == False):
            print("Promenna neexistuje", file=sys.stderr)
            exit(54)

        type = instruction.find('arg2').attrib['type']
        value = instruction.find('arg2').text
        type_of_var = Type.UNDEFINED
        match type:
            case "int":
                value = int(instruction.find('arg2').text)
                type_of_var = Type.INT
            case "string":
                value = instruction.find('arg2').text
                if (value == None):
                    value = ""
                #replacement of escape sequences
                value = re.sub(r'\\([0-9]{3})', lambda match : chr(int(match.group(1))), value)
                type_of_var = Type.STRING
            case "nil":
                value = ""
                type_of_var = Type.NIL
            case "bool":
                value = instruction.find('arg2').text
                type_of_var = Type.BOOL
            case _:
                srcframe, srcname = parseFrameAndName(instruction.find('arg2').text)
                if (checkExistingFrame(srcframe, interpret) == False):
                    print("Ramec neexistuje", file=sys.stderr)
                    exit(55)
                if (checkExistingVar(srcframe, srcname, interpret) == False):
                    print("Promenna neexistuje", file=sys.stderr)
                    exit(54)
                checkInitializedVar(interpret.frames[srcframe][srcname])
                value = interpret.frames[srcframe][srcname]["value"]
                type_of_var = interpret.frames[srcframe][srcname]["type"]
        interpret.frames[frame][name]["value"] = value
        interpret.frames[frame][name]["type"] = type_of_var
    
    def visit_WRITE_DPRINT(self, element, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

        value = handleArgument(instruction, interpret)
        if (type(value) == str):
            #replacement of escape sequences
            value = re.sub(r'\\([0-9]{3})', lambda match : chr(int(match.group(1))), value)

        if (isinstance(element, WRITE)):
            print(value, end='')
        elif (isinstance(element, DPRINT)):
            print(value, file=sys.stderr, end='')
    
    def visit_CREATEFRAME(self, element : CREATEFRAME, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1
        #creates a new TF and the old one (if any exists) is overwritten
        interpret.frames["TF"] = {}

    def visit_PUSHFRAME(self, element : PUSHFRAME, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

        #pushes LF to LFstack and moves TF to LF, TF is deleted
        if (checkExistingFrame("TF", interpret) == True):
            interpret.LFstack.append(interpret.frames["LF"])
            interpret.frames["LF"] = interpret.frames["TF"]
            interpret.frames["TF"] = UNDEFINEDSTACK
        else:
            print("Ramec neexistuje", file=sys.stderr)
            exit(55)

    def visit_POPFRAME(self, element : POPFRAME, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

        #moves LF to TF and then pops LFstack to LF
        if (checkExistingFrame("LF", interpret) == True):
            interpret.frames["TF"] = interpret.frames["LF"]
            if (len(interpret.LFstack) != 0):
                interpret.frames["LF"] = interpret.LFstack.pop()
            else:
                interpret.frames["LF"] = UNDEFINEDSTACK
        else:
            print("Zasobnik lokalnich ramcu je prazdny, POPFRAME nelze provest", file=sys.stderr)
            exit(55)


    def visit_ADD_SUB_MUL_IDIV(self, element, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

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
            if (isinstance(element, ADD)):
                interpret.frames[frame][name]["value"] = int(value_arg2) + int(value_arg3)

            elif(isinstance(element, SUB)):
                interpret.frames[frame][name]["value"] = int(value_arg2) - int(value_arg3)

            elif(isinstance(element, MUL)):
                interpret.frames[frame][name]["value"] = int(value_arg2) * int(value_arg3)

            elif(isinstance(element, IDIV)):
                if (int(value_arg3) == 0):
                    print("Deleni nulou", file=sys.stderr)
                    exit(57)
                interpret.frames[frame][name]["value"] = int(value_arg2) // int(value_arg3)

            interpret.frames[frame][name]["type"] = Type.INT
        else:
            print("Spatne typy operandu", file=sys.stderr)
            exit(53)


    def visit_LT_GT_EQ_AND_OR(self, element, instruction, interpret, operation):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

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
            # 2 nil values are allowed only with operation EQ
            if ((type_arg2 == Type.NIL or type_arg3 == Type.NIL) and (not isinstance(element, EQ))):
                print("Spatny typ operandu", file=sys.stderr)
                exit(53)
            if ((type_arg2 == type_arg3) and (type_arg2 != False) and (type_arg3 != False)):
                if ((isinstance(element, AND) or isinstance(element, OR)) and (type_arg2 != Type.BOOL)):
                    print("Spatny typ operandu", file=sys.stderr)
                    exit(53)
                if (type_arg2 == Type.INT):
                    value_arg2 = int(value_arg2)
                    value_arg3 = int(value_arg3)
                if (((value_arg2 == Type.NIL) and (value_arg3 == Type.NIL)) or
                    (isinstance(element, LT) and (value_arg2 < value_arg3)) or
                    (isinstance(element, GT) and (value_arg2 > value_arg3)) or
                    (isinstance(element, EQ) and (value_arg2 == value_arg3)) or
                    (isinstance(element, AND) and (value_arg2 == "true") and (value_arg3 == "true")) or
                    (isinstance(element, OR) and ((value_arg2 == "true") or (value_arg3 == "true")))):
                        interpret.frames[frame_arg1][name_arg1]["value"] = "true"
                else:
                    interpret.frames[frame_arg1][name_arg1]["value"] = "false"

                interpret.frames[frame_arg1][name_arg1]["type"] = Type.BOOL
            else:
                if ((type_arg2 == Type.NIL) or (type_arg3 == Type.NIL)):
                    interpret.frames[frame_arg1][name_arg1]["value"] = "false"
                    interpret.frames[frame_arg1][name_arg1]["type"] = Type.BOOL
                else:
                    print("Spatny typ operandu", file=sys.stderr)
                    exit(53)
                
    def visit_NOT(self, element : NOT, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

        arg1 = instruction.find('arg1')
        arg2 = instruction.find('arg2')
        frame_arg1, name_arg1 = parseFrameAndName(arg1.text)

        if (checkExistingFrame(frame_arg1, interpret) == False):
            print("Pristup do nedefinovaneho ramce", file=sys.stderr)
            exit(55)
        elif (checkExistingVar(frame_arg1, name_arg1, interpret) == False):
            print("Promenna neexistuje", file=sys.stderr)
            exit(54)
        else:
            type_arg2, value_arg2 = checkSymbTypeAndValue(arg2, interpret)
            if (type_arg2 == Type.BOOL):
                if (value_arg2 == "false"):
                    interpret.frames[frame_arg1][name_arg1]["value"] = "true"
                elif (value_arg2 == "true"):
                    interpret.frames[frame_arg1][name_arg1]["value"] = "false"
                interpret.frames[frame_arg1][name_arg1]["type"] = Type.BOOL
            else:
                print("Spatny typ operandu", file=sys.stderr)
                exit(53)

    def visit_INT2CHAR(self, element, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

        arg1 = instruction.find('arg1')
        arg2 = instruction.find('arg2')
        frame_arg1, name_arg1 = parseFrameAndName(arg1.text)

        if (checkExistingFrame(frame_arg1, interpret) == False):
            print("Pristup do nedefinovaneho ramce", file=sys.stderr)
            exit(55)
        elif (checkExistingVar(frame_arg1, name_arg1, interpret) == False):
            print("Promenna neexistuje", file=sys.stderr)
            exit(54)
        else:
            type_arg2, value_arg2 = checkSymbTypeAndValue(arg2, interpret)
            if (type_arg2 == Type.INT):
                value_arg2 = (int(value_arg2))
                if(0 <= value_arg2 <= 0x10FFFF):    #value_arg2 is a valid character number
                    char_value_arg2 = chr(value_arg2)
                    interpret.frames[frame_arg1][name_arg1]["value"] = char_value_arg2
                    interpret.frames[frame_arg1][name_arg1]["type"] = Type.STRING
                else:
                    print("Chybna prace s retezcem", file=sys.stderr)
                    exit(58)
            else:
                print("Spatny typ operandu", file=sys.stderr)
                exit(53)

    def visit_STRI2INT(self, element, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

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
            if ((type_arg2 == Type.STRING) & (type_arg3 == Type.INT)):
                value_arg3 = int(value_arg3)
                if ((value_arg3 >= 0) and (value_arg3 <= len(value_arg2)-1)):   #value_arg3 must be a valid index in string value_arg2
                    interpret.frames[frame_arg1][name_arg1]["value"] = ord(value_arg2[value_arg3])
                    interpret.frames[frame_arg1][name_arg1]["type"] = Type.INT
                else:
                    print("Chybna prace s retezcem", file=sys.stderr)
                    exit(58)
            else:
                print("Spatny typ operandu", file=sys.stderr)
                exit(53)
            

    def visit_CONCAT(self, element, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

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
            if ((type_arg2 == Type.STRING) and (type_arg3 == Type.STRING)):
                interpret.frames[frame_arg1][name_arg1]["value"] = value_arg2 + value_arg3
                interpret.frames[frame_arg1][name_arg1]["type"] = Type.STRING
            else:
                print("Spatny typ operandu", file=sys.stderr)
                exit(53)

    def visit_STRLEN(self, element, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

        arg1 = instruction.find('arg1')
        arg2 = instruction.find('arg2')
        frame_arg1, name_arg1 = parseFrameAndName(arg1.text)

        if (checkExistingFrame(frame_arg1, interpret) == False):
            print("Pristup do nedefinovaneho ramce", file=sys.stderr)
            exit(55)
        elif (checkExistingVar(frame_arg1, name_arg1, interpret) == False):
            print("Promenna neexistuje", file=sys.stderr)
            exit(54)
        else:
            type_arg2, value_arg2 = checkSymbTypeAndValue(arg2, interpret)
            if (type_arg2 == Type.STRING):
                interpret.frames[frame_arg1][name_arg1]["value"] = len(value_arg2)
                interpret.frames[frame_arg1][name_arg1]["type"] = Type.INT
            else:
                print("Spatny typ operandu", file=sys.stderr)
                exit(53)

    def visit_GETCHAR(self, element, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

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
            if (type_arg2 == Type.STRING and type_arg3 == Type.INT):
                value_arg3 = int(value_arg3)
                if ((value_arg3 >= 0) and (value_arg3 <= len(value_arg2)-1)):   #value_arg3 must be a valid index in string value_arg2
                    interpret.frames[frame_arg1][name_arg1]["value"] = value_arg2[value_arg3]
                    interpret.frames[frame_arg1][name_arg1]["type"] = Type.STRING
                else:
                    print("Chybna prace s retezcem", file=sys.stderr)
                    exit(58)
            else:
                print("Spatny typ operandu", file=sys.stderr)
                exit(53)

    def visit_SETCHAR(self, element, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

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
            type_arg1, value_arg1 = checkSymbTypeAndValue(arg1, interpret)
            type_arg2, value_arg2 = checkSymbTypeAndValue(arg2, interpret)
            type_arg3, value_arg3 = checkSymbTypeAndValue(arg3, interpret)
            if ((type_arg1 == Type.STRING) and (type_arg2 == Type.INT) and (type_arg3 == Type.STRING)):
                value_arg2 = int(value_arg2)
                if ((value_arg2 >= 0) and (value_arg2 <= len(value_arg1)-1) and (len(value_arg3) >= 1)): #value_arg1[value_arg2] = value_arg3[0]
                    interpret.frames[frame_arg1][name_arg1]["value"] = value_arg1[:value_arg2] + value_arg3[0] + value_arg1[value_arg2+1:]
                    interpret.frames[frame_arg1][name_arg1]["type"] = Type.STRING
                else:
                    print("Chybna prace s retezcem", file=sys.stderr)
                    exit(58)
            else:
                print("Spatny typ operandu", file=sys.stderr)
                exit(53)

    def visit_EXIT(self, element, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

        arg1 = instruction.find('arg1')
        type_arg1, value_arg1 = checkSymbTypeAndValue(arg1, interpret)
        if (type_arg1 != Type.INT):
            print("Spatny typ operandu", file=sys.stderr)
            exit(53)
        value_arg1 = int(value_arg1)
        if ((value_arg1 < 0) or (value_arg1 > 49)): #exit code must be a valid number
            print("Spatna hodnota operandu", file=sys.stderr)
            exit(57)
        else:
            exit(value_arg1)
        
    def visit_TYPE(self, element, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

        arg1 = instruction.find('arg1')
        arg2 = instruction.find('arg2')
        frame_arg1, name_arg1 = parseFrameAndName(arg1.text)

        if (checkExistingFrame(frame_arg1, interpret) == False):
            print("Pristup do nedefinovaneho ramce", file=sys.stderr)
            exit(55)
        elif (checkExistingVar(frame_arg1, name_arg1, interpret) == False):
            print("Promenna neexistuje", file=sys.stderr)
            exit(54)
        else:
            is_var, type = isVar(arg2.attrib['type'], arg2.text, interpret)
            if (is_var == True):
                type_arg2 = type
            else:
                is_const, type = isConst(arg2.attrib['type'])
                if (is_const == True):
                        type_arg2 = type

        match type_arg2:
            case Type.UNDEFINED:
                interpret.frames[frame_arg1][name_arg1]["value"] = ""
            case Type.INT:
                interpret.frames[frame_arg1][name_arg1]["value"] = "int"
            case Type.STRING:
                interpret.frames[frame_arg1][name_arg1]["value"] = "string"
            case Type.BOOL:
                interpret.frames[frame_arg1][name_arg1]["value"] = "bool"
            case Type.NIL:
                interpret.frames[frame_arg1][name_arg1]["value"] = "nil"

        interpret.frames[frame_arg1][name_arg1]["type"] = Type.STRING

    def visit_PUSHS(self, element, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

        arg1 = instruction.find('arg1')
        type_arg1, value_arg1 = checkSymbTypeAndValue(arg1, interpret)
        interpret.data_stack.append({"value" : value_arg1, "type" : type_arg1})

    def visit_POPS(self, element, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

        arg1 = instruction.find('arg1')
        frame_arg1, name_arg1 = parseFrameAndName(arg1.text)

        if (checkExistingFrame(frame_arg1, interpret) == False):
            print("Pristup do nedefinovaneho ramce", file=sys.stderr)
            exit(55)
        elif (checkExistingVar(frame_arg1, name_arg1, interpret) == False):
            print("Promenna neexistuje", file=sys.stderr)
            exit(54)

        if (len(interpret.data_stack) != 0):
                interpret.frames[frame_arg1][name_arg1] = interpret.data_stack.pop()
        else:
            print("Datovy zasobnik je prazdny", file=sys.stderr)
            exit(56)

    def visit_BREAK(self, element, instruction, interpret):
        self.op_counter += 1
        printFrames(interpret, instruction.get('order'), self.total_exec_op_cnt)
        self.total_exec_op_cnt += 1

    def visit_LABEL(self, element, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1
        # nothing else to do here since the labels are already saved in the dictionary Interpret.labels

    def visit_JUMP(self, element, instruction, interpret):
        self.total_exec_op_cnt += 1
        if instruction.find('arg1').text in interpret.labels:
            self.op_counter = interpret.labels[instruction.find('arg1').text]
        else:
            print("Pouziti nedefinovaneho navesti", file=sys.stderr)
            exit(52)

    def visit_JUMPIFEQ_JUMPIFNEQ(self, element, instruction, interpret):
        self.total_exec_op_cnt += 1

        arg1 = instruction.find('arg1')
        arg2 = instruction.find('arg2')
        arg3 = instruction.find('arg3')
        if instruction.find('arg1').text not in interpret.labels:
            print("Pouziti nedefinovaneho navesti", file=sys.stderr)
            exit(52)
        else:
            type_arg2, value_arg2 = checkSymbTypeAndValue(arg2, interpret)
            type_arg3, value_arg3 = checkSymbTypeAndValue(arg3, interpret)
            if (((type_arg2 == type_arg3) and (type_arg2 != False) and (type_arg3 != False)) or (type_arg2 ==Type.NIL) or (type_arg3 == Type.NIL)):
                if (type_arg2 == Type.INT):
                    value_arg2 = int(value_arg2)
                if (type_arg3 == Type.INT):
                    value_arg3 = int(value_arg3)
                if ((isinstance(element, JUMPIFEQ) and (value_arg2 == value_arg3)) or (isinstance(element, JUMPIFNEQ) and (value_arg2 != value_arg3))):
                    self.op_counter = interpret.labels[instruction.find('arg1').text]
                else:
                    self.op_counter += 1
            else:
                print("Spatny typ operandu", file=sys.stderr)
                exit(53)

    def visit_CALL(self, element, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

        interpret.call_stack.append(self.op_counter)
        if instruction.find('arg1').text not in interpret.labels:
            print("Pouziti nedefinovaneho navesti", file=sys.stderr)
            exit(52)
        else:
            self.op_counter = interpret.labels[instruction.find('arg1').text]

    def visit_RETURN(self, element, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

        if (len(interpret.call_stack) != 0):
            self.op_counter = interpret.call_stack.pop()
        else:
            #there wasnt any call to return from
            print("Zasobnik volani je prazdny", file=sys.stderr)
            exit(56)

    def visit_READ(self, element, instruction, interpret):
        self.op_counter += 1
        self.total_exec_op_cnt += 1

        radek = ""
        match = False
        arg2 = instruction.find('arg2').text
        if (arg2 != "int" and arg2 != "string" and arg2 != "bool"):
            print("Spatna hodnota operandu", file=sys.stderr)
            exit(57)

        arg1 = instruction.find('arg1').text
        frame_arg1, name_arg1 = parseFrameAndName(arg1)
        if (checkExistingFrame(frame_arg1, interpret) == False):
            print("Pristup do nedefinovaneho ramce", file=sys.stderr)
            exit(55)
        elif (checkExistingVar(frame_arg1, name_arg1, interpret) == False):
            print("Promenna neexistuje", file=sys.stderr)
            exit(54)

        try:
            radek = input()
            match arg2:
                case "int":
                    try:
                        int(radek)
                        match = True
                    except ValueError:
                        match = False
                    if (match):
                        interpret.frames[frame_arg1][name_arg1]["type"] = Type.INT
                case "string":
                        match = True
                        #replacement of escape sequences
                        radek = re.sub(r'\\([0-9]{3})', lambda match : chr(int(match.group(1))), radek)
                        interpret.frames[frame_arg1][name_arg1]["type"] = Type.STRING
                case "bool":
                    match = True
                    if (radek.lower() == "false" or radek.lower() == "true"):
                        radek = radek.lower()
                    else:
                        radek = "false"
                    interpret.frames[frame_arg1][name_arg1]["type"] = Type.BOOL
                case _:
                    print("Spatna hodnota operandu", file=sys.stderr)
                    exit(57)
        except EOFError:
            match = False

        if ((not match)):   #missing or invalid input
            interpret.frames[frame_arg1][name_arg1]["value"] = ""
            interpret.frames[frame_arg1][name_arg1]["type"] = Type.NIL
        else:
            interpret.frames[frame_arg1][name_arg1]["value"] = radek
        