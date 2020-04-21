from cap.plugins import textobjecttypes
from cap.store.textobjectfiles import TextObjectFileGroup, TextObjectFile
from cap.store.textobjects import TextObject
from pathlib import Path
from functools import wraps
import cap.plugins as plugins

LIST_INDEX_PATH = Path('~/.cap/list_index.txt').expanduser()
LIST_PATH = Path('~/.cap/lists').expanduser()

class ListSet:
    def __init__(self, index_path, list_dir):
        self.index = TextObjectFileGroup(index_path)
        self.list_dir = list_dir

    def __len__(self):
        return len(self.index)
    
    def __getitem__(self, key):
        return self.index[key]

    def add(self, list_name, textobjtype):
        self.index.add(TextObjectFile(self.list_dir/f'{list_name}.txt', textobjtype)) 

    def remove(self, list_name):
        self.index.remove(self[list_name])

    def __add__(self, other):
        self.add(*other)
        return self

    def __sub__(self, other):
        self.remove(other)
        return self

    def __delitem__(self, key):
        tof = self[key]
        self.index.delete(tof)
    
    def __iter__(self):
        return iter(self.index)

    def by_name(self):
        return self.index.files_by_name()
    
    def __contains__(self, item):
        return item in self.index

main_list_set = ListSet(LIST_INDEX_PATH, LIST_PATH)

