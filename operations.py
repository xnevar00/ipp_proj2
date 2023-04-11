import abc
from functions import *

class Operation(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def accept(self, visitor, instruction, interpret):
        pass

class DEFVAR(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_DEFVAR(self, instruction, interpret)

class MOVE(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_MOVE(self, instruction, interpret)

class WRITE(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_WRITE_DPRINT(self, instruction, interpret)

class CREATEFRAME(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_CREATEFRAME(self, instruction, interpret)

class PUSHFRAME(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_PUSHFRAME(self, instruction, interpret)

class POPFRAME(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_POPFRAME(self, instruction, interpret)

class ADD(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_ADD_SUB_MUL_IDIV(self, instruction, interpret)

class SUB(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_ADD_SUB_MUL_IDIV(self, instruction, interpret)

class MUL(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_ADD_SUB_MUL_IDIV(self, instruction, interpret)

class IDIV(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_ADD_SUB_MUL_IDIV(self, instruction, interpret)

class LT(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_LT_GT_EQ_AND_OR(self, instruction, interpret, "LT")

class GT(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_LT_GT_EQ_AND_OR(self, instruction, interpret, "GT")

class EQ(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_LT_GT_EQ_AND_OR(self, instruction, interpret, "EQ")

class AND(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_LT_GT_EQ_AND_OR(self, instruction, interpret, "AND")

class OR(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_LT_GT_EQ_AND_OR(self, instruction, interpret, "OR")

class NOT(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_NOT(self, instruction, interpret)

class INT2CHAR(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_INT2CHAR(self, instruction, interpret)

class STRI2INT(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_STRI2INT(self, instruction, interpret)

class CONCAT(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_CONCAT(self, instruction, interpret)

class STRLEN(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_STRLEN(self, instruction, interpret)

class GETCHAR(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_GETCHAR(self, instruction, interpret)

class SETCHAR(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_SETCHAR(self, instruction, interpret)

class EXIT(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_EXIT(self, instruction, interpret)

class TYPE(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_TYPE(self, instruction, interpret)

class DPRINT(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_WRITE_DPRINT(self, instruction, interpret)

class PUSHS(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_PUSHS(self, instruction, interpret)

class POPS(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_POPS(self, instruction, interpret)