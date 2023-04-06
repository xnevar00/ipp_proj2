import argparse
import sys
import xml.etree.ElementTree as et
import abc

class Operation(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def accept(self, visitor, instruction):
        pass

    def checkExistingVar(self, frame, var):
        if var in frames[frame]:
            return True
        else:
            return False
    
    def checkExistingFrame(self, frame):
        if (frames[frame] == None):
            return False
        else:
            return True


class DEFVAR(Operation):
    def accept(self, visitor, instruction):
        visitor.visit_DEFVAR(self, instruction)

class MOVE(Operation):
    def accept(self, visitor, instruction):
        visitor.visit_MOVE(self, instruction)

class WRITE(Operation):
    def accept(self, visitor, instruction):
        visitor.visit_WRITE(self, instruction)

    def handleArgument(self, instruction):
        type = instruction.find('arg1').attrib['type']
        value = instruction.find('arg1').text
        match type:
            case "var":
                var_name_parts = value.split('@')
                frame = var_name_parts[0]
                value = var_name_parts[1]
                if (self.checkExistingVar(frame, value) == True):
                    match frame:
                        case "GF":
                            value = frames["GF"][value]
                        case "LF":
                            value = frames["LF"][value]
                        case "TF":
                            value = frames["TF"][value]
                else:
                    print("Dana promenna neexistuje", file=sys.stderr)
                    exit(54)
            case "nil":
                value = ""
            case "string" | "bool" | "int":
                value = value
        return value

class CREATEFRAME(Operation):
    def accept(self, visitor, instruction):
        visitor.visit_CREATEFRAME(self, instruction)

class PUSHFRAME(Operation):
    def accept(self, visitor, instruction):
        visitor.visit_PUSHFRAME(self, instruction)

class Visitor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def visit_DEFVAR(self, element : DEFVAR, instruction):
        pass

    @abc.abstractmethod
    def visit_MOVE(self, element : MOVE, instruction):
        pass

    @abc.abstractmethod
    def visit_WRITE(self, element : WRITE, instruction):
        pass

    @abc.abstractmethod
    def visit_CREATEFRAME(self, element : CREATEFRAME, instruction):
        pass

    @abc.abstractmethod
    def visit_PUSHFRAME(self, element : PUSHFRAME, instruction):
        pass

class Interpreter(Visitor):
    def visit_DEFVAR(self, element : DEFVAR, instruction):
        var = instruction.find('arg1').text
        var_name_parts = var.split('@')
        frame = var_name_parts[0]
        name = var_name_parts[1]
        if (element.checkExistingFrame(frame) == True):
            if (element.checkExistingVar(frame, name) == False):
                match frame:
                    case "GF":
                        frames["GF"][name] = None
                    case "LF":
                        frames["LF"][name] = None
                    case "TF":
                        frames["TF"][name] = None
            else:
                print("Pokus o definovani jiz existujici promenne", file=sys.stderr)
                exit(52)
        else:
            print("Nelze definovat promennou v neexistujicim ramci", file=sys.stderr)
            exit(55)

    def visit_MOVE(self, element : MOVE, instruction):
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
                value = frames[srcframe][srcname]
        frames[frame][name] = value
    
    def visit_WRITE(self, element : WRITE, instruction):
        value = element.handleArgument(instruction)
        print(value, end='')
    
    def visit_CREATEFRAME(self, element : CREATEFRAME, instruction):
        frames["TF"] = {}

    def visit_PUSHFRAME(self, element : PUSHFRAME, instruction):
        #TODO: presunout aktualni LF na zasobnik a az pak ho nahradit TF
        frames["LF"] = frames["TF"]



def printHelp():
    print("Napoveda k programu interpret.py:\n")
    print("--help          Skript nacte XML reprezentaci programu a tento program s vyuzitim vstupu dle parametru prikazove radky interpretuje a generuje vystup.")
    print("--source=file   Vstupní XML soubor se zdrojovým kódem")
    print("--input=file    Soubor se vstupy")

def initializeArgumentParser():
    parser = argparse.ArgumentParser(description='Popis programu', add_help=False)

    parser.add_argument('--help', action='store_true',
                    help='Skript nacte XML reprezentaci programu a tento program s vyuzitim vstupu dle parametru prikazove radky interpretuje a generuje vystup.')
    parser.add_argument('--source', type=str, metavar='file', help='Vstupní XML soubor se zdrojovým kódem')
    parser.add_argument('--input', type=str, metavar='file', help='Soubor se vstupy')
    return parser

def initializeFrames():
    frames = {"GF" : {}, "LF" : None, "TF" : None}
    return frames

parser = initializeArgumentParser()
args = parser.parse_args()
if (args.help):
    if (len(sys.argv) == 2):
        printHelp()
        exit()
    else:
        print("Parametr --help nelze kombinovat s dalsimi parametry", file=sys.stderr)
        exit(10)
if not (args.source or args.input):
    parser.error('Alespon jeden z parametru --source=file a --input=file je povinny.')

#getting the tree representation of xml file
if (args.source):
    tree = et.parse(args.source)
    root = tree.getroot()
else:
    xml_string = sys.stdin.read()
    root = et.fromstring(xml_string)

# making a dictionary for faster correct order instruction searching
instructions_dict = {}
for instruction in root.findall('.//instruction[@order]'):
    order = instruction.get('order')
    instructions_dict[order] = instruction

frames = initializeFrames()

#initialization of operation classes
defvar = DEFVAR()
move = MOVE()
write = WRITE()
create_frame = CREATEFRAME()

#initialization of visitor interpreter
interpreter = Interpreter()

for order, instruction in instructions_dict.items():
    opcode = instruction.get('opcode')
    match opcode:
        case "DEFVAR":
            defvar.accept(interpreter, instruction)
        case "MOVE":
            move.accept(interpreter, instruction)
        case "WRITE":
            write.accept(interpreter, instruction)
        case "CREATEFRAME":
            create_frame.accept(interpreter, instruction)

