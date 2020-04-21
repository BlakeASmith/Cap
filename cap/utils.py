
def subclasses(cls):
    for subcls in cls.__subclasses__():
        yield subcls
        yield from subclasses(subcls)
