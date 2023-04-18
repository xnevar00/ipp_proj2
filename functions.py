#           IPP projekt 2
#
# author:   Veronika Nevarilova (xnevar00)
# date:     4/2022
# file:     functions.py

import sys
from enum import Enum
import re

class Type(Enum):
    UNDEFINED = 0
    INT = 1
    STRING = 2
    BOOL = 3
    NIL = 4

UNDEFINEDSTACK = -1

# "GF@a" => "GF", "a"
def parseFrameAndName(arg):
    var_name_parts = arg.split('@')
    frame = var_name_parts[0]
    name = var_name_parts[1]
    return frame, name

# serves for WRITE operation, returns value to print
def handleArgument(instruction, interpret):
        type = instruction.find('arg1').attrib['type']
        value = instruction.find('arg1').text
        match type:
            case "var":
                frame, name = parseFrameAndName(value)
                if (checkExistingFrame(frame, interpret) == False):
                    print("Dany ramec neexistuje", file=sys.stderr)
                    exit(55)
                if (checkExistingVar(frame, name, interpret) == True):
                    checkInitializedVar(interpret.frames[frame][name])
                    match frame:
                        case "GF":
                            if (interpret.frames["GF"][name]["type"] == Type.NIL):
                                value = ""
                            else:
                                value = interpret.frames["GF"][name]["value"]
                        case "LF":
                            if (interpret.frames["LF"][name]["type"] == Type.NIL):
                                value = ""
                            else:
                                value = interpret.frames["LF"][name]["value"]
                        case "TF":
                            if (interpret.frames["TF"][name]["type"] == Type.NIL):
                                value = ""
                            else:
                                value = interpret.frames["TF"][name]["value"]
                else:
                    print("Dana promenna neexistuje", file=sys.stderr)
                    exit(54)
            case "nil":
                value = ""
            case "string" | "bool" | "int":
                value = value
        return value

# checks whether the given variable already exists or not
def checkExistingVar(frame, var, interpret):
    if var in interpret.frames[frame]:
        return True
    else:
        return False

#checks whether the given frame already exists or not and if its not an invalid frame  
def checkExistingFrame(frame, interpret):
    if (frame != "GF" and frame != "LF" and frame != "TF"):
        print("Neexistujici ramec", file=sys.stderr)
        exit(52)

    if (interpret.frames[frame] == UNDEFINEDSTACK):
        return False
    else:
        return True

# returns the type of variable
def getTypeOfVar(frame, var, interpreter):
    if (checkExistingFrame(frame, interpreter)):
        if (checkExistingVar(frame, var, interpreter)):
            return interpreter.frames[frame][var]["type"]
        else:
            print("Neexistujici promenna", file=sys.stderr)
            exit(54)
    else:
        print("Neexistujici ramec", file=sys.stderr)
        exit(55)

# check whether an instruction argument is a variable or not
def isVar(type, name, interpret):
    match type:
        case "var":
            frame, name = parseFrameAndName(name)
            if (checkExistingFrame(frame, interpret) == True):
                if (checkExistingVar(frame, name, interpret) == True):
                    return True, interpret.frames[frame][name]["type"]
                else:
                    print("Neexistujici promenna", file=sys.stderr)
                    exit(54)
            else:
                print("Neexistujici ramec", file=sys.stderr)
                exit(55)
        case _:
            return False, Type.UNDEFINED

# check whether an instructioin argument is a constant or not    
def isConst(type):
    match type:
        case "nil":
            return True, Type.NIL
        case "string":
            return True, Type.STRING
        case "bool":
            return True, Type.BOOL
        case "int":
            return True, Type.INT
        case _:
            return False, Type.UNDEFINED

#returns a value of a variable, if it exists        
def getValue(frame, name, interpreter):
    if (checkExistingFrame(frame) == True):
        if (checkExistingVar(frame, name) == True):
            return interpreter.frames[frame][name]["value"]
        else:
            print("Neexistujici promenna", file=sys.stderr)
            exit(54)
    else:
        print("Neexistujici ramec", file=sys.stderr)
        exit(55)

# check, if the given argument is whether existing var in an aexisting frame or a constant.
# returns its type and value. The caller must cast the value himself, if he wants to use it!
def checkSymbTypeAndValue(arg, interpret):
    is_var, type = isVar(arg.attrib['type'], arg.text, interpret)

    if (is_var == True):
        frame, name = parseFrameAndName(arg.text)
        checkInitializedVar(interpret.frames[frame][name])
        return type, interpret.frames[frame][name]["value"]
    else:
        is_const, type = isConst(arg.attrib['type'])
        if (is_const == True):
                if (arg.text == None and type == Type.STRING):
                    return type, ""
                elif (type == Type.STRING):
                    value = re.sub(r'\\([0-9]{3})', lambda match : chr(int(match.group(1))), arg.text)
                    return type, value
                else:
                    return type, arg.text
        else: 
            return False, -1
        
# check if there was already inserted value to the variable. If not, the program stops with according error code
def checkInitializedVar(var):
    if (var["type"] == Type.UNDEFINED):
        print("Chybejici hodnota", file=sys.stderr)
        exit(56)

#serves for debug print (operation BREAK)
def typeToString(type):
    match type:
        case Type.INT:
            return "int"
        case Type.STRING:
            return "string"
        case Type.BOOL:
            return "bool"
        case Type.NIL:
            return "nil"
        case Type.UNDEFINED:
            return "***"

#debug print for operation BREAK    
def printFrame(frame, interpret):
    print("*************   "+ frame +"   **************")
    if (checkExistingFrame(frame, interpret) == False):
        print("          *doesn't exist*")
    else:
        print("{:<15}{:<15}{}".format("NAME", "TYPE", "VALUE"))
        print("")
        for var in interpret.frames[frame]:
            type = typeToString(interpret.frames[frame][var]["type"])
            if (type == "***"):
                value = "***"
            else:
                value = interpret.frames[frame][var]["value"]
            print("{:<15}{:<15}{}".format(var, type, value))

#debuf print for operation BREAK
def printFrames(interpret, opcode_num, total_exec_op_count):
    print("Pozice v kodu: operace c. " + opcode_num)
    print("Pocet provedenych operaci: " + str(total_exec_op_count))

    printFrame("GF", interpret)
    print("\n")
    printFrame("LF", interpret)
    print("\n")
    printFrame("TF", interpret)

    