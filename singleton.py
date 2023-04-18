class Singleton(type):
    _instances = {}

    def call(cls, args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).call(args, **kwargs)
        return cls._instances[cls]