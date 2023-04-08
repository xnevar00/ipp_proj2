import sys
from enum import Enum

class Type(Enum):
    UNDEFINED = 0
    INT = 1
    STRING = 2
    BOOL = 3
    NIL = 4

UNDEFINEDSTACK = -1

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
                    checkInitializedVar(interpret.frames[frame][name])
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

#pro vyhodnoceni, zda argument v instrukci je promenna nebo konstanta
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
# vraci jeji typ a hodnotu. Volajici si musi hodnotu sam pretypovat pokud s ni chce pracovat!
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
                else:
                    return type, arg.text
        else: 
            return False, -1
        
#kontroluje, zda byla do promenne vlozena hodnota. Pokud ne, ukonci program s odpovidajici chybou
def checkInitializedVar(var):
    if (var["type"] == Type.UNDEFINED):
        print("Chybejici hodnota", file=sys.stderr)
        exit(56)

