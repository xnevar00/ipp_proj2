import argparse
import sys
import xml.etree.ElementTree as et
from visitor import *

UNDEFINEDSTACK = -1

class Interpret:
    def __init__(self):
        self.parser = self.initializeArgumentParser()
        self.args = self.parser.parse_args()
        self.frames, self.LFstack = self.initializeFrames()

    def printHelp(self):
        print("Napoveda k programu interpret.py:\n")
        print("--help          Skript nacte XML reprezentaci programu a tento program s vyuzitim vstupu dle parametru prikazove radky interpretuje a generuje vystup.")
        print("--source=file   Vstupní XML soubor se zdrojovým kódem")
        print("--input=file    Soubor se vstupy")

    def initializeArgumentParser(self):
        parser = argparse.ArgumentParser(description='Popis programu', add_help=False)

        parser.add_argument('--help', action='store_true',
                        help='Skript nacte XML reprezentaci programu a tento program s vyuzitim vstupu dle parametru prikazove radky interpretuje a generuje vystup.')
        parser.add_argument('--source', type=str, metavar='file', help='Vstupní XML soubor se zdrojovým kódem')
        parser.add_argument('--input', type=str, metavar='file', help='Soubor se vstupy')
        return parser

    def initializeFrames(self):
        frames = {"GF" : {}, "LF" : UNDEFINEDSTACK, "TF" : UNDEFINEDSTACK}
        LFstack = []
        return frames, LFstack
    
    def interpret(self):
        if (self.args.help):
            if (len(sys.argv) == 2):
                self.printHelp()
                exit()
            else:
                print("Parametr --help nelze kombinovat s dalsimi parametry", file=sys.stderr)
                exit(10)
        if not (self.args.source or self.args.input):
            self.parser.error('Alespon jeden z parametru --source=file a --input=file je povinny.')

        #getting the tree representation of xml file
        if (self.args.source):
            tree = et.parse(self.args.source)
            root = tree.getroot()
        else:
            xml_string = sys.stdin.read()
            root = et.fromstring(xml_string)

        # making a dictionary for faster correct order instruction searching
        instructions_dict = {}
        for instruction in root.findall('.//instruction[@order]'):
            order = instruction.get('order')
            instructions_dict[order] = instruction


        #initialization of operation classes
        defvar = DEFVAR()
        move = MOVE()
        write = WRITE()
        create_frame = CREATEFRAME()
        push_frame = PUSHFRAME()
        pop_frame = POPFRAME()
        add = ADD()
        sub = SUB()
        mul = MUL()
        idiv = IDIV()
        lt = LT()
        gt = GT()
        eq = EQ()

        #initialization of visitor interpreter
        interpreter = Interpreter()

        for order, instruction in instructions_dict.items():
            opcode = instruction.get('opcode')
            match opcode:
                case "DEFVAR":
                    defvar.accept(interpreter, instruction, self)
                case "MOVE":
                    move.accept(interpreter, instruction, self)
                case "WRITE":
                    write.accept(interpreter, instruction, self)
                case "CREATEFRAME":
                    create_frame.accept(interpreter, instruction, self)
                case "PUSHFRAME":
                    push_frame.accept(interpreter, instruction, self)
                case "POPFRAME":
                    pop_frame.accept(interpreter, instruction, self)
                case "ADD":
                    add.accept(interpreter, instruction, self)
                case "SUB":
                    sub.accept(interpreter, instruction, self)
                case "MUL":
                    mul.accept(interpreter, instruction, self)
                case "IDIV":
                    idiv.accept(interpreter, instruction, self)
                case "LT":
                    lt.accept(interpreter, instruction, self)
                case "GT":
                    gt.accept(interpreter, instruction, self)
                case "EQ":
                    eq.accept(interpreter, instruction, self)
                

