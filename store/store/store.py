from pathlib import Path
from string import Template
from types import SimpleNamespace
from createhook import hooks
import re


_SL = Path(__file__).parent / 'stores_list.txt'
SL_entry = lambda n, p, pat: f'{n} {p} {pat}'

def SL_entry_pattern(name='^[a-zA-Z0-9]+', path=r'\S*', pattern='.*' ):
    return re.compile((
            r'^\s*(?P<name>{})\s+'
            r'(?P<path>{})\s\s*'
            r'(?P<pattern>{})\s*$'
    ).format(name, path, pattern), re.MULTILINE)


head = lambda name, pattern: f"""
Name:          {name}
Pattern:       {pattern}

"""

def stores(*names):
    matches = SL_entry_pattern().finditer(_SL.read_text())
    if matches is None:
        raise ValueError(f"none of these stores: {names} exist ")
    all_stores     = [SimpleNamespace(**m.groupdict()) for m in matches]
    stores_by_name = {store.name:store for store in all_stores}
    for name in names:
        if name not in stores_by_name:
            raise ValueError(f'there is no store called {name}')
    matching_stores = [store for name, store
            in stores_by_name.items() if name in names]
    for store in matching_stores:
        store.pattern = re.compile(store.pattern, re.MULTILINE)
    if len(names) == 1: return matching_stores[0]
    return matching_stores

@hooks.before
@hooks.after
def create(name, path, pattern):
    # create an entry in the stores list
    with _SL.open(mode='a') as stores:
        print(SL_entry(name, path, pattern), file=stores)
    # create a new store
    Path(path).write_text(head(name, pattern))

@hooks.before
@hooks.after
def delete(store_name):
    def raise_error():
        raise ValueError(
        f'''there is no store with name: {store_name}
            {stores()}
        ''')
    store_pattern = SL_entry_pattern(name=store_name)
    stores_text = _SL.read_text()
    match = store_pattern.search(stores_text)
    store = match.groupdict() if match is not None else raise_error()
    try:Path(store['path']).unlink()
    except FileNotFoundError:raise_error()
    finally: _SL.write_text(stores_text[:match.start(0)]
            + stores_text[match.end(0):])


def check(store_name, data):
    store = stores(store_name)
    match = store.pattern.match(data)
    if match is None: raise ValueError(f"""
    {data}
    does not match pattern {store.pattern} of store {store_name}
    """)
    return store


@hooks.before
@hooks.after
def add(store_name, data):
    store = check(store_name, data)
    with open(store.path, 'a') as st:
        print(data, file=st)

def __remove(store_name, data):
    store = check(store_name, data)
    path = Path(store.path)
    text = path.read_text()
    match = store.pattern.search(data)
    if match is None:
        raise ValueError(f"""
        {data}
        the given entry is not present in store {store_name}
        """)
    start, end = match.span(0)
    path.write_text(text[:start] + text[end:])
    return (start, end)

@hooks.before
@hooks.after
def remove(store_name, data):
    __remove(store_name, data)


@hooks.before
@hooks.after
def replace(store_name, data):
    store = check(store_name, data)
    start, end = __remove(store_name, data)
    path = Path(store.path)
    text = path.read_text()
    path.write_text(text[:start] + data + text[start:])

@hooks.before
@hooks.after
def all_entries(store_name):
    store = stores(store_name)
    path = Path(store.path)
    matches = store.pattern.finditer(path.read_text())
    return [match.group(0) for match in matches]


@hooks.before
@hooks.after
def search(store_name, pattern):
    all_matches = all_entries(store_name)
    return [match for match in all_matches
            if re.match(pattern, match, re.MULTILINE)]




