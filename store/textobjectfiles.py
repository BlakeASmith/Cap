from pathlib import Path
from createhook import hooks
import re
import textobjects
import hooks


class TextObjectFile:
    """A file which contains instances of a TextObject

    Attributes:
        textobjectcls (class): the subclass of `textobjects.TextObject` which is
            stored in the file

        path (:obj: pathlib.Path): the path to the file where `textobjectcls`
            occurances are / should be stored
    """
    def __init__(self, path, textobjectcls):
        self.textobjectcls = textobjectcls
        self.path = Path(path)
        if not self.path.exists():
            self.path.write_text('')

    def entries(self, as_genorator=False):
        genorator = self.textobjectcls.findall(self.path.read_text())
        return genorator if as_genorator else list(genorator)

    def add(self, *items):
        with self.path.open('a') as f:
            for item in items:
                if self.textobjectcls.match(str(item)):
                    print(str(item), file=f)
                else:
                    raise ValueError(f"{item} is not a {self.textobjectcls}")

    def remove(self, *items):
        text = self.path.read_text()
        for item in [str(it) for it in items]:
            if not self.textobjectcls.match(item):
                raise ValueError(f"{item} is not a {self.textobjectcls}")
            text = text.replace(item, '')
        self.path.write_text(text)

    def replace(self, item, new_item):
        item, new_item, text = str(item), str(new_item), self.path.read_text() 
        if not self.textobjectcls.match(item) and self.textobjectcls.match(new_item):
            raise ValueError(f'either {item} for {new_item} is not a {self.textobjectcls}')
        self.path.write_text(text.replace(item, new_item))


class TextObjectFileGroupEntry(textobjects.RegexTextObject):
    @staticmethod
    def regex():
        return re.compile('(?P<path>.*) (?P<textobjcls>.*)')

    def __str__(self):
        return f'{self.path} {self.textobjcls.__name__}'

    def __init__(self, path, textobjcls):
        self.path = path
        if type(textobjcls) is str:
            self.textobjcls = next((subcls for subcls in textobjects.RegexTextObject.__subclasses__() if subcls.__name__ == textobjcls))
        else:
            self.textobjcls = textobjcls



class TextObjectFileGroup:
    def __init__(self, path):
        self.file = TextObjectFile(path, TextObjectFileGroupEntry)

    
    def add(self, *textobjectfiles):
        """add a TextObjectFile to the group

        Args:
            textobjectfile (:obj: TextObjectFile) the TextObjectFile to add to the group
        """
        self.file.add(*[TextObjectFileGroupEntry(textobjectfile.path, textobjectfile.textobjectcls) for textobjectfile in textobjectfiles])

    def remove(self, *textobjectfiles):
        """remove a file from the registry

        Args:
            filepath(:obj: pathlib.Path) the path to the file to be removed
        """
        self.file.remove(*[TextObjectFileGroupEntry(textobjfile.path, textobjfile.textobjectcls) for textobjfile in textobjectfiles])

    def files_in_group(self):
        return [TextObjectFile(entry.path, entry.textobjcls) for entry in self.file.entries()]

    def entries(self):
        for textobjfile in self.files_in_group():
            yield from textobjfile.entries()


