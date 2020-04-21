from pathlib import Path
import re
from cap.store.textobjects import *
from cap.utils import subclasses
from cap.plugins import textobjecttypes


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
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.touch()

    def entries(self):
        yield from [textobj for textobj in self.textobjectcls.findall(self.path.read_text())]

    def __iter__(self):
        return self.entries

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
            txtobj = self.textobjectcls.match(item)
            if not txtobj:
                raise ValueError(f"{item} is not a {self.textobjectcls}")
            if not re.search(str(txtobj), text):
                raise ValueError(f"{txtobj} is not in the file \n{text}")
            text = text.replace(item, '')
        self.path.write_text(text)

    def replace(self, item, new_item):
        item, new_item, text = str(item), str(new_item), self.path.read_text() 
        if not self.textobjectcls.match(item) and self.textobjectcls.match(new_item):
            raise ValueError(f'either {item} for {new_item} is not a {self.textobjectcls}')
        self.path.write_text(text.replace(item, new_item))

    def delete(self):
        """ delete the file"""
        self.path.unlink()

    def __len__(self):
        return len(self.__iter__())
    
    def __getitem__(self, key):
        return self.__iter__()[key]
    
    def __setitem__(self, key, value):
        item = self[key]
        self.replace(item, value)
    
    def __delitem__(self, key):
        self.remove(self[key])
    
    def __iter__(self):
        return self.entries()
    
    def __contains__(self, item):
        return item in self.__iter__()

    def append(self, items):
        items = list(items)
        self.add(*items)
        return self

    def __add__(self, other):
        other = list(other)
        return self.append(*other)

    def __sub__(self, other):
        other = list(other)
        self.remove(*other)
        return self
        
@constructed_text_object('$path $textobjcls')
class TextObjectFileGroupEntry:
    def transform(txtobj):
        txtobj.path = Path(txtobj.path)
        txtobj.textobjcls = textobjecttypes[txtobj.textobjcls]

    def str_from_args(self, path, txtobject):
        if isinstance(path, Path):
            path = str(path)
        if not isinstance(txtobject, str):
            txtobject = txtobject.__name__
        return f'{path} {txtobject}'


class TextObjectFileGroup:
    def __init__(self, path):
        self.file = TextObjectFile(path, TextObjectFileGroupEntry)
    
    def add(self, *textobjectfiles):
        """add a TextObjectFile to the group

        Args:
            textobjectfile (:obj: TextObjectFile) the TextObjectFile to add to the group
        """
        self.file.add(*[TextObjectFileGroupEntry(textobjectfile.path, textobjectfile.textobjectcls) 
            for textobjectfile in textobjectfiles])

    def remove(self, *textobjectfiles):
        """remove a file from the registry

        Args:
            filepath(:obj: pathlib.Path) the path to the file to be removed
        """
        self.file.remove(*[TextObjectFileGroupEntry(textobjfile.path, textobjfile.textobjectcls) 
            for textobjfile in textobjectfiles])

    def delete(self, *textobjectfiles):
        """completly delete a TextObjectFile

        Args: 
            *textobjectfiles (:obj: TextObjectFile): the text object files to delete
        """
        for textobjectfile in textobjectfiles:
            textobjectfile.delete()
            self.remove(textobjectfile)

    def files_by_name(self):
        return {tof.path.with_suffix('').name:tof for tof in self}

    def __len__(self):
        return len(self.__iter__())

    def __getitem__(self, key):
        return self.files_by_name()[key]
    
    def __iter__(self):
        return iter([TextObjectFile(entry.path, entry.textobjcls) for entry in self.file.entries()])
    
    def __contains__(self, item):
        return str(item) in self.file.entries() or str(item) in self.files_by_name()

    def entries(self):
        for textobjfile in self.files_in_group():
            yield from textobjfile.entries()


