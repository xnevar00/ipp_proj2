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
        visitor.visit_WRITE(self, instruction, interpret)

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
        visitor.visit_ADD_SUB_MUL_IDIV(self, instruction, interpret, "ADD")

class SUB(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_ADD_SUB_MUL_IDIV(self, instruction, interpret, "SUB")

class MUL(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_ADD_SUB_MUL_IDIV(self, instruction, interpret, "MUL")

class IDIV(Operation):
    def accept(self, visitor, instruction, interpret):
        visitor.visit_ADD_SUB_MUL_IDIV(self, instruction, interpret, "IDIV")

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