import sys
from enum import Enum

class Type(Enum):
    UNDEFINED = 0
    INT = 1
    STRING = 2
    BOOL = 3
    NIL = 4

UNDEFINEDSTACK = -1
UNDEFINEDTYPE  = -2

def parseFrameAndName(arg):
    var_name_parts = arg.split('@')
    frame = var_name_parts[0]
    name = var_name_parts[1]
    return frame, name

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
                    match frame:
                        case "GF":
                            value = interpret.frames["GF"][name]["value"]
                        case "LF":
                            value = interpret.frames["LF"][name]["value"]
                        case "TF":
                            value = interpret.frames["TF"][name]["value"]
                else:
                    print("Dana promenna neexistuje", file=sys.stderr)
                    exit(54)
            case "nil":
                value = ""
            case "string" | "bool" | "int":
                value = value
        return value

def checkExistingVar(frame, var, interpret):
    if var in interpret.frames[frame]:
        return True
    else:
        return False
    
def checkExistingFrame(frame, interpret):
    if (interpret.frames[frame] == UNDEFINEDSTACK):
        return False
    else:
        return True

def checkType(var, type):
    match type:
        case "int":
            if (var["type"] == Type.INT):
                return True
        case "bool":
            if (var["type"] == Type.BOOL):
                return True
        case "string":
            if (var["type"] == Type.STRING):
                return True
        case "nil":
            if (var["type"] == Type.NIL):
                return True
        case "undefined":
            if (var["type"] == Type.UNDEFINED):
                return True
    return False

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

# kontroluje, zda zadany argument je bud existujici promenna v existujicim ramci, nebo konstanta.
# vraci bool a hodnotu. Volajici si musi hodnotu sam pretypovat pokud s ni chce pracovat!
def checkSymbTypeAndValue(arg, type, interpret):
    is_var2, type2 = isVar(arg.attrib['type'], arg.text, interpret)

    if (is_var2 == True):
        if (type2 != type):
            print("Spatne typy operandu", file=sys.stderr)
            exit(53)
        else:
            frame, name = parseFrameAndName(arg.text)
            return True, interpret.frames[frame][name]["value"]
    else:
        is_const2, type2 = isConst(arg.attrib['type'])
        if (is_const2 == True):
            if ( type2 != type):
                print("Spatne typy operandu", file=sys.stderr)
                exit(53)
            else:
                return True, arg.text
        else: 
            return False, -1

