from abc import *
import re

class Plugin(ABC):

    @property
    @abstractmethod
    def TextObjectType(self):
        """a subclass of TextObject"""
        pass

class TextObject(ABC):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if self.attr_checks[key](val):
                setattr(self, key, val)
            else: raise TypeError

    @property
    @abstractmethod
    def attr_checks(self):
        """A dictionary with attribute names as keys and
        functions which check the validity of the attribute as
        values. This is used to ensure that the class is not
        instantiated with invalid attribues"""
        pass

    @property
    @abstractmethod
    def pattern(self):
        """Regex pattern used to identify this TextObject"""
        pass



