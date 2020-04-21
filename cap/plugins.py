from cap.store.textobjects import TextObject, RegexTextObject
from cap.utils import subclasses
from pathlib import Path
from importlib.machinery import SourceFileLoader
from pathlib import Path

PLUGINS_DIR = Path('~/.cap/plugins').expanduser()

def __module(path):
    """load a module from the specified path"""
    name = path.with_suffix('').name
    return SourceFileLoader(name, str(path)).load_module()

modules = [__module(p) for p in PLUGINS_DIR.glob('*.py')]

textobjecttypes = {cls.__name__:cls for cls in subclasses(TextObject) 
        if cls is not TextObject and cls is not RegexTextObject}


