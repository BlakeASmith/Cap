""":name: store Tests for store.py"""
import sys
import unittest
from pathlib import Path
import store
from textobjects import ToDo

STORES_DIR = Path('/tmp/stores')
if not STORES_DIR.exists():
    STORES_DIR.mkdir()


class TestTextObjectFile(unittest.TestCase):
    def test(self):
        todos = store.TextObjectFile(STORES_DIR/'todo.txt', ToDo)
        todos.path.write_text('')

        todo = ToDo("todo1")
        todos.add(todo)
        todos.add(ToDo('another todo'))

        todo1, todo2 = todos.entries()
        assert todo1.item == 'todo1'
        assert todo2.item == 'another todo'

        todos.remove(todo2, todo1)
        assert not todos.entries()

        todos.add(todo1)
        todos.replace(todo1, todo2)

        todo = todos.entries()[0]
        assert todo.item == todo2.item

        todos.path.write_text('')

class TestTextObjectFileGroup(unittest.TestCase):
    def test(self):
        todolist1 = store.TextObjectFile(STORES_DIR/'todolist1.txt', ToDo)
        todolist2 = store.TextObjectFile(STORES_DIR/'todolist2.txt', ToDo)
        todolist3 = store.TextObjectFile(STORES_DIR/'todolist3.txt', ToDo)
        
        masterlist = store.TextObjectFileGroup(STORES_DIR/'todogroup.txt')
        masterlist.file.path.write_text("")
        masterlist.add(todolist1, todolist2, todolist3)
        masterlist.remove(todolist2)
        todolist1.add(ToDo('foo'), ToDo('bar'), ToDo('cat'))
        todolist2.add(ToDo('foobar'), ToDo('barfoo'))

        print(masterlist.files_in_group())
        for e1, e2 in zip(list(todolist1.entries()) + list(todolist2.entries()), 
                list(masterlist.entries())):
            assert e1 == e2






if __name__ == '__main__':
    unittest.main()
