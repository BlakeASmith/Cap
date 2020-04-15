import sys
from pathlib import Path
path = str(Path(__file__).parent.parent)
sys.path.append(path)
import unittest
from store import store

stores_dir = '/tmp/stores'
stores_dir_path = Path(stores_dir)
if not stores_dir_path.exists(): stores_dir_path.mkdir()

class TestStore(unittest.TestCase):
    def test1(self):
        store_name = 'test1'
        store_path = f'{stores_dir}/test1'
        store_patt = r'^.*$'

        hook_called = False

        @store.create.before
        def before_create(name, path, pattern):
            print(name, path, pattern)
            nonlocal hook_called
            hook_called = True

        store.create(store_name, store_path, store_patt)
        store_text = Path(store_path).read_text()
        assert(store_text == store.head(store_name, store_patt))
        store.delete(store_name)
        try:
            store.delete(store_name)
            assert(False)
        except ValueError:
            pass
        assert(not Path(store_path).exists())
        assert(store._SL.read_text() == '')
        assert(hook_called)

    def test2(self):
        store_name = 'test2'
        store_path = f'{stores_dir}/test2'
        store_patt = r'^.*$'
        store.create(store_name, store_path, store_patt)
        data1, data2 = 'fooobar', 'barfoo'

        store.add(store_name, data1)
        store.add(store_name, data2)
        entries = store.search(store_name, data1)
        assert(entries[0] == data1)
        to_remove = store.search(store_name, '.*bar.*foo')
        store.remove(store_name, to_remove)
        assert(data2 not in store.all(store_name))
        store.remove(store_name, data1)
        assert(data1 not in store.all(store_name))
        store.delete(store_name)

if __name__ == '__main__':
    unittest.main()
