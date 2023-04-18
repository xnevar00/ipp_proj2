import sys

class XmlChecker:

    def __init__(self):
        self.XMLOK = 0
        self.XMLERR = -1


    #implementovano:
    #       kontrola jestli kazda instrukce obsahuje opcode a order
    #       kontrola jestli neni mezi instrukcema nejaky random bordel
    #       kontrola, jestli neni nejaky order dvakrat
    #       kontrola, jestli neni opocode zaporny
    #       kontrola, jestli je order jen cele cislo >= 1
    #       odchytavani vyjimek xml parseru, tedy check, zda je xml soubor well formed
    #       kontrola, jestli je v instrukci spravny pocet argumentu a jestli jde cislovani od 1
    #       kontrola, zda kazdy atribut instrukce obsahuje 'type'

    #kontrola, zda instrukce nemaji nejake atributy navic
    def checkXml(self, root, instruction_list):
        self.checkRoot(root)

        # Projde všechny instrukce ve stromu
        for instr in root.findall('.//instruction[@order][@opcode]'):

            # Získání atributu order
            order = instr.get('order')
            order = order.strip()

            #kontrola, zda je to jen cele kladne cislo
            if (not order.isdigit()):
                print("Neocekavana struktura XML", file=sys.stderr)
                exit(32)
            order = int(order)

            #kontrola, zda neni order uz v nejake instrukci predtim nebo order neni zaporny
            if (self.isAlreadyUsed(instruction_list, order) or order <= 0):
                print("Neocekavana struktura XML", file=sys.stderr)
                exit(32)
            
            # Přidání názvu operace do seznamu
            instr = self.removeSpaces(instr)
            data = {"order": order, "instruction": instr}
            instruction_list.append(data)

        # pokud se nerovna pocet deti programu (instrukci) s nactenymi instrukcemi, znamena to, ze je tam jeste nejaka jina vec, nepriklad argument povalujici se nahodne
        # venku z instrukce
        if (len(root) != len(instruction_list)):
            print("Neocekavana struktura XML", file=sys.stderr)
            exit(32)

        self.checkNumberOfArguments(instruction_list)

        return instruction_list

    def checkRoot(self, root):
        if ((root.tag == 'program') and ('language' in root.attrib) and (root.attrib['language'] == 'IPPcode23')):
            return
        else:
            print("Neocekavana struktura XML", file=sys.stderr)
            exit(32)

    def isAlreadyUsed(self, instruction_list, order):
        for instr in instruction_list:
            if instr.get('order') == order:
                return True
            else:
                return False
        
    def checkNumberOfArguments(self, instruction_list):
        for instr in instruction_list:
            instruction = instr.get('instruction')
            opcode = instruction.get('opcode')
            opcode = opcode.upper()
            ok = False

            match opcode:
                case "CREATEFRAME" | "PUSHFRAME" | "POPFRAME" | "RETURN" | "BREAK":
                    if ((len(instruction) == 0)):
                        ok = True
                case "DEFVAR" | "POPS":
                    if ((len(instruction) == 1) and (instruction.find('arg1') is not None) and self.checkExistingTypeInAtribs(instruction) and self.isVar(instruction.find('arg1'))):
                            ok = True
                case "CALL" | "LABEL" | "JUMP":
                    if ((len(instruction) == 1) and (instruction.find('arg1') is not None) and self.checkExistingTypeInAtribs(instruction) and self.isLabel(instruction.find('arg1'))):
                            ok = True
                case  "PUSHS" | "WRITE" | "EXIT" | "DPRINT":
                    if ((len(instruction) == 1) and (instruction.find('arg1') is not None) and self.checkExistingTypeInAtribs(instruction) and self.isSymb(instruction.find('arg1'))):
                            ok = True
                case "MOVE" | "INT2CHAR" | "STRLEN" | "TYPE" | "NOT":
                    if ((len(instruction) == 2) and (instruction.find('arg1') is not None) and (instruction.find('arg2') is not None) and self.checkExistingTypeInAtribs(instruction) and self.isVar(instruction.find('arg1')) and self.isSymb(instruction.find('arg2'))):
                            ok = True
                case "READ":
                    if ((len(instruction) == 2) and (instruction.find('arg1') is not None) and (instruction.find('arg2') is not None) and self.checkExistingTypeInAtribs(instruction) and self.isVar(instruction.find('arg1')) and self.isType(instruction.find('arg2'))):
                            ok = True
                case "ADD" | "SUB" | "MUL" | "IDIV" | "LT" | "GT" | "EQ" | "AND" | "OR" | "STRI2INT" | "CONCAT" | "GETCHAR" | "SETCHAR":
                      if ((len(instruction) == 3)and (instruction.find('arg1') is not None) and (instruction.find('arg2') is not None) and (instruction.find('arg3') is not None) and self.checkExistingTypeInAtribs(instruction) and self.isVar(instruction.find('arg1')) and self.isSymb(instruction.find('arg2')) and self.isSymb(instruction.find('arg3'))):
                            ok = True
                case  "JUMPIFEQ" | "JUMPIFNEQ":
                    if ((len(instruction) == 3)and (instruction.find('arg1') is not None) and (instruction.find('arg2') is not None) and (instruction.find('arg3') is not None) and self.checkExistingTypeInAtribs(instruction) and self.isLabel(instruction.find('arg1')) and self.isSymb(instruction.find('arg2')) and self.isSymb(instruction.find('arg3'))):
                            ok = True

            if (ok == False):
                print("Neocekavana struktura XML", file=sys.stderr)
                exit(32)
    
    def checkExistingTypeInAtribs(self, instruction):
        for arg_element in instruction:
            if 'type' not in arg_element.attrib:
                return False
        return True

    def isSymb(self, arg):
        match arg.attrib.get('type') :
            case "var" | "int" | "bool" | "string" | "nil":
                return True
            case _:
                return False
    
    def isLabel(self, arg):
        if (arg.attrib.get('type')  == "label"):
            return True
        else:
            return False
    
    def isType(self, arg):
        if (arg.attrib.get('type')  == "type"):
            return True
        else:
            return False
        
    def isVar(self, arg):
        if (arg.attrib.get('type') == "var"):
            return True
        else:
            return False
        
    def removeSpaces(self, instruction):
        for arg in instruction:
            if (arg.text is not None):
                arg.text = arg.text.strip()

        return instruction