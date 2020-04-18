from abc import ABC, abstractmethod, abstractproperty
import re

class TextObject(ABC):
    """An object which can be represented in plain text"""

    @abstractmethod
    def __str__(self):
        """produce the plain text representation of the object"""

    def __eq__(self, other):
        return str(self) == str(other)

    @classmethod
    @abstractmethod
    def from_text(cls, text):
        """product an instance of the object from the text representation
        Args:
            text (str): the text to convert into a TextObject

        Raises:
            ValueError if `text` does not represent a TextObject
        """

    @classmethod
    @abstractmethod
    def match(self, text):
        """matches a `text_object` at the beginning of the text.
        similar to `re.match`

        Args:
            text (str): The text to match

        Returns:
            an instance of `text_object` if the text matches, otherwise None
        """

    @classmethod
    @abstractmethod
    def search(self, text):
        """search for a `text_object` within some text. and return
        the first occurance found

        Args:
            text (str): The text to search

        Returns:
            an instance of `text_obect` if found, else None
        """

    @classmethod
    @abstractmethod
    def findall(self, text):
        """find all occurances of `text_object` in the text

        Args:
            text (str): The text to be searched

        Returns:
            a list of `text_object` instances which were found
        """

class RegexTextObject(TextObject):
    """A TextObject based on a regex. The attributes of 
    the object are based on the named groups of the regex

    Note: any subclass must be able to be instantiated with only the 
        arguments from the named groups of the regex as it is created 
        internally using `__init__(**groups)` where `groups` is a dictionary
        containing the named groups of the regex produced by the `regex` method

    Args: 
        **groups: 
    """

    @staticmethod
    @abstractmethod
    def regex(*args, **kwargs):
        """produce an `re.RegexObject` which will match the text object

        Returns:
            a (:obj: re.RegexObject) which will match the desired text object
        """
        pass

    @abstractmethod
    def __init__(*args, **kwargs):
        """__init__ must have an argument for each of the 
        named groups in the regex produced by `cls.regex()`.
        any arguments that do not correspond to a named group
        must be optional
        """
        pass

    @classmethod
    def __from_groups(cls, **groups):
        return cls(**groups)

    @classmethod
    def from_text(cls, text):
        """produce an instance of the RegexTextObject from a string"""
        match = cls.regex().match(text)
        if not match: raise ValueError(f"{text} is not a valid {cls}")
        return cls.__from_groups(**match.groupdict())

    @classmethod
    def match(cls, text):
        """match some text against the regex for this RegexTextObject
        and return an instance if it matches

        Args:
            text (str): the text to match
        Returns:
            an instance of this RegexTextObject or None
        """
        try:
            return cls.from_text(text)
        except ValueError:
            return None

    @classmethod
    def search(cls, text, include_match_object=False):
        """search for a match to the regex for this RegexTextObject 
        in the given text and return an instance if found.

        Args:
            text (str): the text to search
            include_match_object (bool): if true the re.MatchObject will be returned
                along with the match

        Returns: 
            an instance of this RegexTextObject if found, or None if not found
            if `include_match_object` is True the return will be a tuple 
            (MatchObject, RegexTextObject)
        """
        match = cls.regex().search(text)
        if match:
            instance = cls.__from_groups(**match.groupdict()) 
            return (match, instance) if include_match_object else instance


    @classmethod
    def findall(cls, text, include_match_objects=False):
        """find all matches of the regex for this RegexTextObject and
        return an instance for each found"""
        matches = cls.regex().finditer(text)
        if not matches: raise ValueError(f"there were no matches in the given text")
        if include_match_objects:
            return ((m, cls.__from_groups(**m.groupdict())) for m in matches)
        else:
            return (cls.__from_groups(**m.groupdict()) for m in matches)

    
class ToDo(RegexTextObject):

    def __init__(self, item):
        self.item = item
    
    @staticmethod
    def regex():
        return re.compile('^\s*TODO: (?P<item>.*)$', re.MULTILINE)

    def __str__(self):
        return f'TODO: {self.item}'

    def __repr__(self):
        return f'ToDo(\"{self.item}\")'

