""":name: tests.test_store Tests for store.py"""
import sys
import unittest
from pathlib import Path
import store


STORES_DIR = '/tmp/stores'
STORES_DIR_PATH = Path(STORES_DIR)
if not STORES_DIR_PATH.exists():
    STORES_DIR_PATH.mkdir()

class TestStore(unittest.TestCase):
    def test1(self):
        store_name = 'test1'
        store_path = Path(f'{STORES_DIR}/test1')
        store_patt = r'^.*$'

        hook_called = False

        @store.create.before
        def before_create(name, path, pattern):
            print(name, path, pattern)
            nonlocal hook_called
            hook_called = True

        store.create(store_name, store_path, store_patt)
        store_text = store_path.read_text()
        assert store_text == store.head(store_name, store_patt)
        store.delete(store_name)
        try:
            store.delete(store_name)
            assert False
        except ValueError:
            pass
        assert not Path(store_path).exists()
        assert store._SL.read_text() == ''
        assert hook_called

    def test2(self):
        store_name = 'test2first'
        store_path = f'{STORES_DIR}/test2'
        store_patt = r'^.*$'
        store2_name = 'test2second'
        store2_path = f'{STORES_DIR}/test2second'
        store2_patt = r'^.*$'
        data1, data2 = 'this is data 1', 'this is data 2'
        store.create(store_name, store_path, store_patt)
        store.create(store2_name, store2_path, store2_patt)
        try:
            created1, created2 = store.get(store_name, store2_name)
            assert store_path == str(created1.path)
            assert store_path == str(created1.path)
            assert store_patt == created1.pattern.pattern
            assert store2_path == str(created2.path)
            assert store2_path == str(created2.path)
            assert store2_patt == created2.pattern.pattern

            store.add(store_name, data1)
            store.add(store_name, data2)
            entry1, entry2 = store.get_entries(store_name)
            print(entry1, data1)
            store.add(store2_name, data1, data2)
            print(store.get_entries(store_name, store2_name))


        except Exception as exception:
            store.delete(store_name, store2_name)
            raise exception

        store.delete(store_name, store2_name)
        assert store._SL.read_text() == ''


if __name__ == '__main__':
    unittest.main()
