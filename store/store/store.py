from pathlib import Path
from string import Template
from types import SimpleNamespace
from createhook import hooks
import re

_SL = Path(__file__).parent / 'store_index.txt'
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

def list_all():
    """lists all the stores
    Returns:
        a namespace with the following attributes
        ::
            {
                'name (str)': the name of the store
                'path (pathlib.Path)': the path of the store
                'pattern (re.RegexObject)': the regex pattern of the
                    entries in the store
            }
     """
    matches = SL_entry_pattern().finditer(_SL.read_text())
    if matches is None: return None
    stores = [SimpleNamespace(**m.groupdict()) for m in matches]
    for store in stores:
        store.pattern = re.compile(store.pattern, re.MULTILINE)
        store.path    = Path(store.path)
    return stores


def get(*names):
    """get the name, path, and pattern for each of the specified stores

    Args:
        name: the name of the desired stores
        *names (str): the names of any additional desired stores

    Returns:
        a list of namespaces containing the attributes
        ::
            {
                'name (str)': the name of the store
                'path (pathlib.Path)': the path of the store
                'pattern (re.RegexObject)': the regex pattern of the
                    entries in the store
            }

    Raises:
        ValueError: if stores do not exist for any of the given names
    """

    stores_by_name = {store.name:store for store in list_all()}

    for name in names:
        if name not in stores_by_name:
            raise ValueError(f'there is no store called {name}')

    return [store for name, store in stores_by_name.items() if name in names]


def entries(*store_names, groups=False, include_store_found=False):
    """get all entries from a store

    Args:
        store_name (str): the name of the store
        groups (bool): if True, a dictionary containing the named groups of
            the stores regex pattern will be returned along with each entry
        include_store_found: if True the store which the entry was found will be included
            in the return

    Returns:
        a dict with the store names as keys and the entries as values.
        if the `groups` option is set the values will be a list of tuples with (text, groupdict).
        `text` is the text of the entry and `groupdict` is a dictionary containing the
        named groups of the stores regex for the entry. otherwise the values are lists of strings.

        if only one store name is given the return will be only a list of entries
    """
    entries = {}
    for store in get(*store_names):
        text = store.path.read_text().replace(head(store.name, store.pattern.pattern), '')
        matching = [(m.group(0), m.groupdict()) if groups else m.group(0)
                for m in store.pattern.finditer(text) if m.group(0) != '']
        entries[store.name] = matching
    if len(store_names) == 1: return entries[store_names[0]]
    else: return entries


@hooks.before
@hooks.after
def create(name, path, pattern):
    """create a new store

    Args:
        name (str): the name of the store
        path (str): the location of the store
        pattern (str): the regex pattern which the entries of the
            store will match

    """
    # create an entry in the get list
    with _SL.open(mode='a') as get:
        print(SL_entry(name, path, pattern), file=get)
    # create a new store
    Path(path).write_text(head(name, pattern))

@hooks.before
@hooks.after
def delete(name, *store_names):
    """delete a store, or multiple stores

    Args:
        name (str): name of the store to delete
        *store_names: names of any additional stores to delete

    Raises:
        ValueError: when there is no store with any one of the given names
    """
    store_names = (name,) + store_names
    for store_name in store_names:
        def raise_error():
            raise ValueError(
            f'''there is no store with name: {store_name}
                {list_all()}
            ''')
        store_pattern = SL_entry_pattern(name=store_name)
        get_text = _SL.read_text()
        match = store_pattern.search(get_text)
        store = match.groupdict() if match is not None else raise_error()
        try:Path(store['path']).unlink()
        except FileNotFoundError:raise_error()
        finally: _SL.write_text(get_text[:match.start(0)]
                + get_text[match.end(0):])


def check(store_name, *entries):
    """check that a given entry is valid for a given store

    Args:
        store_name (str): the name of the store
        *entries (str): the entries to be cheked

    Raises:
        ValueError: when the given store does not exist
        ValueError: when andy of the given entries is not valid for the store.
            (it does not match the regex pattern of the store)

    """
    store = get(store_name)[0]
    for entry in entries:
        match = store.pattern.match(entry)
        if match is None: raise ValueError(f"""
        {entry}
        does not match pattern {store.pattern} of store {store_name}
        """)
    return store


@hooks.before
@hooks.after
def add(store_name, *entries):
    """add the given item to the given store

    Args:
        store_name (str): the name of the store to add the entries to
        *entries (str): the entries to add to the store

    Raises:
        ValueError: when any of the given entries does not match the regex for
            the store
    """
    store = check(store_name, *entries)
    with open(store.path, 'a') as st:
        for entry in entries:
            print(entry, file=st)

def __remove(store_name, *entries):
    store = check(store_name, *entries)
    text = store.path.read_text()
    locations = []
    for entry in entries:
        match = store.pattern.search(entry)
        if match is None:
            raise ValueError(f"""
            {data}
            the given entry is not present in store {store_name}
            """)
        start, end = match.span(0)
        store.path.write_text(text[:start] + text[end:])
        locations.append((start,end))
    return locations

@hooks.before
@hooks.after
def remove(store_name, *entries):
    """remove the given entries from the store

    Args:
        store_name (str): the store to remove the entries from
        *entries (str): the entries to be removed

    Raises:
        ValueError: when the given store does not exist or
            any of the given entries are not valid entries in
            the store. (they do not match the regex pattern of
            the store)

    """
    __remove(store_name, *entries)


@hooks.before
@hooks.after
def replace(store_name, *entries):
    store = check(store_name, *entries)
    locations = __remove(store_name, *entries)
    for start, _ in locations:
        text = store.path.read_text()
        store.path.write_text(text[:start] + data + text[start:])


@hooks.before
@hooks.after
def search(*store_names, pattern):
    matches_by_store = {name: [match for match in st_entries if re.match(pattern, match, re.MULTILINE)]
            for name, st_entries in entries(*store_names).items()}
    if len(store_names) == 1: return matches_by_store[store_names[0]]
    else: return matches_by_store




