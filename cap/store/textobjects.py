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

    def __format__(self, args):
        return format(str(self), args)

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

    def __init__(self, text=None,  match=None):
        if not match:
            match = self.regex.search(text)
        for k,v in match.groupdict().items():
            setattr(self, k , v)
        self.span = match.span
        self.text = match.group(0)
        self.groups = match.groups()[1:]
        self.transformations()

    @classmethod
    def _from_match(cls, match):
        return cls(match=match)

    def _transformations(self):
        pass

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
        return cls._from_match(match)

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
            return cls._from_match(match)

    @classmethod
    def findall(cls, text):
        """find all matches of the regex for this RegexTextObject and
        return an instance for each found"""
        matches = cls.regex.finditer(text)
        if not matches: raise ValueError(f"there were no matches in the given text")
        return [cls._from_match(m) for m in matches]

def textobject(name, template):
    """create a RegexTextObject subclass based on 
    the template

    Args: 
        name (str): this will be the name of the created class
        template (str): TODO

    Returns:
        a decorator function TODO
    """
    def createtxtobj(func):
        attrmarker = r"{(\w*):'(.*?)'}"
        tokenmarker = r'\$(\S+(?=\s*))'
        toksubbed = re.sub(tokenmarker, '(?P<\g<1>>.*)~', template)
        patsubbed = re.sub(attrmarker, '(?P<\g<1>>\g<2>)~', toksubbed)
        regex = patsubbed.replace('~', r'\s*')


        class txtobj(RegexTextObject, regex=regex):

            def transformations(self):
                func(self)

        txtobj.__name__ = name
        txtobj.__qualname__ = name
        return txtobj
    return createtxtobj

def createtxtobj(name, template):
    return textobject(name, template)(lambda x:x)

def constructed_text_object(template):
    def construct_text_object(cls, name='', template=template):
        txtobj = createtxtobj(name, template)
        if hasattr(cls, 'transform'):
            txtobj.transformations = cls.transform

        for name, val in vars(cls).items():
            if not name.startswith('__'):
                setattr(txtobj, name, val)

        for attr in dir(cls):
            if not hasattr(txtobj, attr):
                setattr(txtobj, attr, getattr(cls, attr))

        txtobj.__name__ = cls.__name__
        txtobj.__qualname__ = cls.__qualname__

        @wraps(txtobj.__init__)
        def newinit(self, *args, text=None, match='no match', **kwargs):
            if match == 'no match' and text is None:
                match = txtobj.regex.search(self.str_from_args(*args, **kwargs))
            elif text:
                match = txtobj.regex.search(text)
            if not match: raise ValueError(f'{text} is not a valid {txtobj.__name__}')
            super(txtobj, self).__init__(match=match)

        txtobj.__init__ = newinit
        return txtobj
    return construct_text_object

@constructed_text_object('TODO: $item')
class ToDo:
    def str_from_args(self, item):
        return f'TODO: {item} {self.foo}'

Line = createtxtobj('Line', '^.*$')
