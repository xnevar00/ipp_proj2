import argparse
import sys
import xml.etree.ElementTree as et
from visitor import *
from xmlChecker import *

UNDEFINEDSTACK = -1

class Interpret:
    def __init__(self):
        self.parser = self.initializeArgumentParser()
        self.args = self.parser.parse_args()
        self.frames, self.LFstack = self.initializeFrames()
        self.data_stack = self.initializeDataStack()
        self.call_stack = self.initializeCallStack()
        self.labels = {}

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
                xml_string = sys.stdin.read()
                root = et.fromstring(xml_string)
            except et.ParseError:
                print("Chybny XML format ve vstupnim souboru", file=sys.stderr)
                sys.exit(31)

        
        sourceFile = sys.stdin
        if (self.args.input):
            try:
                sys.stdin = open(self.args.input, "r")
            except FileNotFoundError:
                print("Soubor se nepodarilo otevrit.", file=sys.stderr)
                sys.exit(11)
            
        # Vytvoření seznamu pro instrukce
        xml_checker = XmlChecker()
        instrukce = []
        instrukce = XmlChecker.checkXml(xml_checker, root, instrukce)

        # Seřazení seznamu podle order atributu
        self.labels = {}
        instrukce = sorted(instrukce, key=lambda x: x["order"])
        operation_count = 0
        for instr in instrukce:
            if (instr.get('instruction').get('opcode') == "LABEL"):
                if (instr.get('instruction').find('arg1').text not in self.labels):
                    self.labels[instr.get('instruction').find('arg1').text] = operation_count
                else:
                    print("Redefinice promenne", file=sys.stderr)
                    sys.exit(52)
            operation_count += 1

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
        and_op = AND()
        or_op = OR()
        not_op = NOT()
        int2char = INT2CHAR()
        stri2int = STRI2INT()
        concat = CONCAT()
        strlen = STRLEN()
        getchar = GETCHAR()
        setchar = SETCHAR()
        exit = EXIT()
        type = TYPE()
        dprint = DPRINT()
        pushs = PUSHS()
        pops = POPS()
        break_op = BREAK()
        label = LABEL()
        jump = JUMP()
        jumpifeq = JUMPIFEQ()
        jumpifneq = JUMPIFNEQ()
        call = CALL()
        return_op = RETURN()
        read = READ()

        #initialization of visitor interpreter
        interpreter = Interpreter()

        while (interpreter.op_counter <= len(instrukce) -1):
            instruction = instrukce[interpreter.op_counter]["instruction"]
            opcode = instruction.get('opcode')
            opcode = opcode.upper()
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
                case "AND":
                    and_op.accept(interpreter, instruction, self)
                case "OR":
                    or_op.accept(interpreter, instruction, self)
                case "NOT":
                    not_op.accept(interpreter, instruction, self)
                case "INT2CHAR":
                    int2char.accept(interpreter, instruction, self)
                case "STRI2INT":
                    stri2int.accept(interpreter, instruction, self)
                case "CONCAT":
                    concat.accept(interpreter, instruction, self)
                case "STRLEN":
                    strlen.accept(interpreter, instruction, self)
                case "GETCHAR":
                    getchar.accept(interpreter, instruction, self)
                case "SETCHAR":
                    setchar.accept(interpreter, instruction, self)
                case "EXIT":
                    exit.accept(interpreter, instruction, self)
                case "TYPE":
                    type.accept(interpreter, instruction, self)  
                case "DPRINT":
                    dprint.accept(interpreter, instruction, self)
                case "PUSHS":
                    pushs.accept(interpreter, instruction, self)
                case "POPS":
                    pops.accept(interpreter, instruction, self)
                case "BREAK":
                    break_op.accept(interpreter, instruction, self)
                case "LABEL":
                    label.accept(interpreter, instruction, self)
                case "JUMP":
                    jump.accept(interpreter, instruction, self)
                case "JUMPIFEQ":
                    jumpifeq.accept(interpreter, instruction, self)
                case "JUMPIFNEQ":
                    jumpifneq.accept(interpreter, instruction, self)
                case "CALL":
                    call.accept(interpreter, instruction, self)
                case "RETURN":
                    return_op.accept(interpreter, instruction, self)
                case "READ":
                    read.accept(interpreter, instruction, self)
                case _:
                    sys.exit()

