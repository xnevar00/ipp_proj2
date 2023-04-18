#           IPP projekt 2
#
# author:   Veronika Nevarilova (xnevar00)
# date:     4/2022
# file:     classInterpret.py

import argparse
import sys
import xml.etree.ElementTree as et
from visitor import *
from xmlChecker import *
from singleton import *

UNDEFINEDSTACK = -1

class Interpret(metaclass = Singleton):
    def __init__(self):
        self.parser = self.initializeArgumentParser()
        self.args = self.parser.parse_args()
        self.frames, self.LFstack = self.initializeFrames()
        self.data_stack = self.initializeDataStack()
        self.call_stack = self.initializeCallStack()
        self.labels = {}

        self.operation_dict = {
            "DEFVAR": DEFVAR(),
            "MOVE" : MOVE(),
            "WRITE" : WRITE(),
            "CREATEFRAME" : CREATEFRAME(),
            "PUSHFRAME" : PUSHFRAME(),
            "POPFRAME" : POPFRAME(),
            "ADD" : ADD(),
            "SUB" : SUB(),
            "MUL" : MUL(),
            "IDIV" : IDIV(),
            "LT" : LT(),
            "GT" : GT(),
            "EQ" : EQ(),
            "AND" : AND(),
            "OR" : OR(),
            "NOT": NOT(),
            "INT2CHAR" : INT2CHAR(),
            "STRI2INT" : STRI2INT(),
            "CONCAT" : CONCAT(),
            "STRLEN" : STRLEN(),
            "GETCHAR" : GETCHAR(),
            "SETCHAR" : SETCHAR(),
            "EXIT" : EXIT(),
            "TYPE" : TYPE(),
            "DPRINT" : DPRINT(),
            "PUSHS" : PUSHS(),
            "POPS" : POPS(),
            "BREAK" : BREAK(),
            "LABEL" : LABEL(),
            "JUMP" : JUMP(),
            "JUMPIFEQ" : JUMPIFEQ(),
            "JUMPIFNEQ" : JUMPIFNEQ(),
            "CALL" : CALL(),
            "RETURN" : RETURN(),
            "READ" : READ()}

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
    
    def initializeDataStack(self):
        data_stack = []
        return data_stack
    
    def initializeCallStack(self):
        call_stack = []
        return call_stack
    
    def interpret(self):
        if (self.args.help):
            if (len(sys.argv) == 2):
                self.printHelp()
                sys.exit()
            else:
                print("Parametr --help nelze kombinovat s dalsimi parametry", file=sys.stderr)
                sys.exit(10)
        if not (self.args.source or self.args.input):
            self.parser.error('Alespon jeden z parametru --source=file a --input=file je povinny.')

        #getting the tree representation of xml file
        if (self.args.source):
            try:
                file = open(self.args.source, "r")
            except FileNotFoundError or PermissionError:
                print("Soubor se nepodarilo otevrit.", file=sys.stderr)
                sys.exit(11)
            try:
                tree = et.parse(file)
                root = tree.getroot()
            except et.ParseError:
                print("Chybny XML format ve vstupnim souboru", file=sys.stderr)
                sys.exit(31)
        else:
            try:
                # when no source given, it gets data from stdin
                xml_string = sys.stdin.read()
                root = et.fromstring(xml_string)
            except et.ParseError:
                print("Chybny XML format ve vstupnim souboru", file=sys.stderr)
                sys.exit(31)

        if (self.args.input):
            try:
                # when no input given, it gets data from stdin
                sys.stdin = open(self.args.input, "r")
            except FileNotFoundError:
                print("Soubor se nepodarilo otevrit.", file=sys.stderr)
                sys.exit(11)
    
        xml_checker = XmlChecker()
        # making a list for instructions
        instructions = []
        #getting the xml file representation checked
        instructions = XmlChecker.checkXml(xml_checker, root, instructions)

        self.labels = {}
        # ordering the list by attribute 'order'
        instructions = sorted(instructions, key=lambda x: x["order"])
        operation_count = 0

        # loading labels to a dictionary for an easier access in case of jumps in program
        for instr in instructions:
            if (instr.get('instruction').get('opcode') == "LABEL"):
                if (instr.get('instruction').find('arg1').text not in self.labels):
                    self.labels[instr.get('instruction').find('arg1').text] = operation_count
                else:
                    print("Redefinice promenne", file=sys.stderr)
                    sys.exit(52)
            operation_count += 1

        #initialization of visitor interpreter
        interpreter = Interpreter()

        while (interpreter.op_counter <= len(instructions) -1):
            instruction = instructions[interpreter.op_counter]["instruction"]
            opcode = instruction.get('opcode')
            opcode = opcode.upper()
            operation = self.operation_dict.get(opcode)
            if (operation is None):
                print("Neexistujici operace", file=sys.stderr)
                sys.exit(32)
            else:
                operation.accept(interpreter, instruction, self)

