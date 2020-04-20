from abc import ABC, abstractmethod, abstractproperty
from functools import wraps
from inspect import signature
from createhook import hooks
import re

class TextObject(ABC):
    """An object which can be represented in plain text"""

    @abstractmethod
    def __str__(self):
        """produce the plain text representation of the object"""

    def __eq__(self, other):
        return str(self) == str(other)

    def __len__(self):
        return len(str(self))

    def __iter__(self):
        return iter(str(self))

    def __contains__(self, other):
        return other in str(self)

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
            a list of instances of TextObject
        """

class RegexTextObject(TextObject):
    """A TextObject based on a regex. The attributes of 
    the object are the named groups of the regex

    Args: 
        **groups: 
    """

    def __init_subclass__(cls, regex, flags=[re.MULTILINE],  **kwargs):
        super.__init_subclass__(**kwargs)
        cls.regex = re.compile(regex, *flags)

    def __init__(self, enclosing_text, match=None):
        self.enclosing_text = enclosing_text
        if not match:
            match = self.regex.search(enclosing_text)
        if not match: raise ValueError(f"{enclosing_text} is not a valid {self.__class__}")
        for k,v in match.groupdict().items():
            setattr(self, k , v)
        self.text = match.group(0)
        self.span = match.span

    def __str__(self):
        return self.text

    @classmethod
    def match(cls, text):
        """match some text against the regex for this RegexTextObject
        and return an instance if it matches

        Args:
            text (str): the text to match
        Returns:
            an instance of this RegexTextObject or None
        """
        match = cls.regex.match(text)
        if not match: raise ValueError(f"{text} is not a valid {cls}")
        return cls(text, match)

    @classmethod
    def search(cls, text):
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
        match = cls.regex.search(text)
        if match:
            return cls(text, match)

    @classmethod
    def findall(cls, text):
        """find all matches of the regex for this RegexTextObject and
        return an instance for each found"""
        matches = cls.regex.finditer(text)
        if not matches: raise ValueError(f"there were no matches in the given text")
        return [cls(text, match) for m in matches]
    

def textobject(name, template):
    """create a RegexTextObject subclass with
    based on the template"""
    regexmarker = '\r<(.*?)>'
    attrmarker = r"{(\w*):'(.*?)'}"
    tokenmarker = r'\$(\S*(?=\s*))'
    regexsubbed = re.sub(regexmarker, '\g<1>', template)
    toksubbed = re.sub(tokenmarker, '(?P<\g<1>>.*)~', regexsubbed)
    patsubbed = re.sub(attrmarker, '(?P<\g<1>>\g<2>)~', toksubbed)
    regex = patsubbed.replace('~', r'\s*')
    print(regex)

    text = re.sub(tokenmarker, '{}', template)
    text = re.sub(attrmarker, '{}', text)
    text = re.sub(regexmarker, '', text)

    class txtobj(RegexTextObject, regex=regex):
        def __init__(self, *args, **kwargs):
            super(txtobj, self).__init__(text.format(*args))
        
    txtobj.__name__
    return txtobj


