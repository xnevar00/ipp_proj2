#           IPP projekt 2
#
# author:   Veronika Nevarilova (xnevar00)
# date:     4/2022
# file:     singleton.py

class Singleton(type):
    _instances = {}

    def call(cls, args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).call(args, **kwargs)
        return cls._instances[cls]