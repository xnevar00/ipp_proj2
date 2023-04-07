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
        visitor.visit_ADD(self, instruction, interpret)
