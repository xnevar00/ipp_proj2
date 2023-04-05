import argparse
import sys
import xml.etree.ElementTree as et

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
    GF = {}
    LF = {}
    TF = {}
    frames = {"GF" : GF, "LF" : LF, "TF" : TF}
    return frames

def interpretDEFVAR(instruction):
    var = instruction.find('arg1').text
    var_name_parts = var.split('@')
    frame = var_name_parts[0]
    name = var_name_parts[1]
    if (name not in frames[frame]):
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

def interpretMOVE(instruction):
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

for order, instruction in instructions_dict.items():
    opcode = instruction.get('opcode')
    match opcode:
        case "DEFVAR":
            interpretDEFVAR(instruction)
        case "MOVE":
            interpretMOVE(instruction)
        case "WRITE":
            print("mam write")

print(frames["GF"]["a"])