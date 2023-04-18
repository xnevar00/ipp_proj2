#           IPP projekt 2
#
# author:   Veronika Nevarilova (xnevar00)
# date:     4/2022
# file:     xmlChecker.py

import sys

class XmlChecker:

    def __init__(self):
        self.XMLOK = 0
        self.XMLERR = -1

    #xml format check
    def checkXml(self, root, instruction_list):
        self.checkRoot(root)

        # iterates through all the instructions that have attribute order and opcode
        for instr in root.findall('.//instruction[@order][@opcode]'):

            order = instr.get('order')

            #removing occasional spaces
            order = order.strip()

            #check if order is only an integer
            if (not order.isdigit()):
                print("Neocekavana struktura XML", file=sys.stderr)
                exit(32)
            order = int(order)

            #there must not be two instructions with the same order number
            if (self.isAlreadyUsed(instruction_list, order) or order <= 0):
                print("Neocekavana struktura XML", file=sys.stderr)
                exit(32)
            
            # adding the operation to the list
            instr = self.removeSpaces(instr)
            data = {"order": order, "instruction": instr}
            instruction_list.append(data)

        # if the number of 'program' children and loaded instructions with order and opcode doesnt match,
        # it means that there is either some trash between the instructions or an instruction without
        # order or opcode
        if (len(root) != len(instruction_list)):
            print("Neocekavana struktura XML", file=sys.stderr)
            exit(32)

        self.checkArguments(instruction_list)

        return instruction_list

    #check if the root has all mandatory things
    def checkRoot(self, root):
        if ((root.tag == 'program') and ('language' in root.attrib) and (root.attrib['language'] == 'IPPcode23')):
            return
        else:
            print("Neocekavana struktura XML", file=sys.stderr)
            exit(32)

    #returns true if there is already an instruction with the same order
    def isAlreadyUsed(self, instruction_list, order):
        for instr in instruction_list:
            if instr.get('order') == order:
                return True
            else:
                return False

    #check if arguments are correctly given    
    def checkArguments(self, instruction_list):
        for instr in instruction_list:
            instruction = instr.get('instruction')
            opcode = instruction.get('opcode')
            opcode = opcode.upper()
            ok = False

            match opcode:
                #instructions with 0 arguments wanted
                case "CREATEFRAME" | "PUSHFRAME" | "POPFRAME" | "RETURN" | "BREAK":
                    if ((len(instruction) == 0)):
                        ok = True

                #instructions with 1 argument 'var' wanted
                case "DEFVAR" | "POPS":
                    if ((len(instruction) == 1) and (instruction.find('arg1') is not None) and self.checkExistingTypeInArgs(instruction) and self.isVar(instruction.find('arg1'))):
                            ok = True
                
                #instructions with 1 argument 'label' wanted
                case "CALL" | "LABEL" | "JUMP":
                    if ((len(instruction) == 1) and (instruction.find('arg1') is not None) and self.checkExistingTypeInArgs(instruction) and self.isLabel(instruction.find('arg1'))):
                            ok = True
                #instructions with 1 argument 'symb' wanted
                case  "PUSHS" | "WRITE" | "EXIT" | "DPRINT":
                    if ((len(instruction) == 1) and (instruction.find('arg1') is not None) and self.checkExistingTypeInArgs(instruction) and self.isSymb(instruction.find('arg1'))):
                            ok = True
                
                #instructions with 2 arguments 'var' and 'symb' wanted
                case "MOVE" | "INT2CHAR" | "STRLEN" | "TYPE" | "NOT":
                    if ((len(instruction) == 2) and (instruction.find('arg1') is not None) and (instruction.find('arg2') is not None) and self.checkExistingTypeInArgs(instruction) and self.isVar(instruction.find('arg1')) and self.isSymb(instruction.find('arg2'))):
                            ok = True
                
                #instructions with 2 arguments 'var' and 'type' wanted
                case "READ":
                    if ((len(instruction) == 2) and (instruction.find('arg1') is not None) and (instruction.find('arg2') is not None) and self.checkExistingTypeInArgs(instruction) and self.isVar(instruction.find('arg1')) and self.isType(instruction.find('arg2'))):
                            ok = True

                #instructions with 3 arguments 'var' and 'symb' and 'symb' wanted
                case "ADD" | "SUB" | "MUL" | "IDIV" | "LT" | "GT" | "EQ" | "AND" | "OR" | "STRI2INT" | "CONCAT" | "GETCHAR" | "SETCHAR":
                      if ((len(instruction) == 3)and (instruction.find('arg1') is not None) and (instruction.find('arg2') is not None) and (instruction.find('arg3') is not None) and self.checkExistingTypeInArgs(instruction) and self.isVar(instruction.find('arg1')) and self.isSymb(instruction.find('arg2')) and self.isSymb(instruction.find('arg3'))):
                            ok = True

                #instructions with 3 argument 'label' and 'symb' and 'symb' wanted
                case  "JUMPIFEQ" | "JUMPIFNEQ":
                    if ((len(instruction) == 3)and (instruction.find('arg1') is not None) and (instruction.find('arg2') is not None) and (instruction.find('arg3') is not None) and self.checkExistingTypeInArgs(instruction) and self.isLabel(instruction.find('arg1')) and self.isSymb(instruction.find('arg2')) and self.isSymb(instruction.find('arg3'))):
                            ok = True

            if (ok == False):
                print("Neocekavana struktura XML", file=sys.stderr)
                exit(32)
    
    # check if every argument has a mandatory attribute 'type'
    def checkExistingTypeInArgs(self, instruction):
        for arg_element in instruction:
            if 'type' not in arg_element.attrib:
                return False
        return True

    # returns true if a type of an argument is symb
    def isSymb(self, arg):
        match arg.attrib.get('type') :
            case "var" | "int" | "bool" | "string" | "nil":
                return True
            case _:
                return False
    
    # returns true if a type of an argument is label
    def isLabel(self, arg):
        if (arg.attrib.get('type')  == "label"):
            return True
        else:
            return False
    
    # returns true if a type of an argument is type
    def isType(self, arg):
        if (arg.attrib.get('type')  == "type"):
            return True
        else:
            return False
        
    # returns true if a type of an argument is var
    def isVar(self, arg):
        if (arg.attrib.get('type') == "var"):
            return True
        else:
            return False
    
    # removes spaces from every argument text
    def removeSpaces(self, instruction):
        for arg in instruction:
            if (arg.text is not None):
                arg.text = arg.text.strip()

        return instruction