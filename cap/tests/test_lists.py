from cap.lists import lists
from cap.store.textobjects import ToDo
from cap.lists.lists import ListSet
from pathlib import Path
import unittest


class TestLists(unittest.TestCase):
    def test_add(self):
        testlistset = ListSet(Path('/tmp/testlistset.txt'), Path('/tmp/testlists'))
        testlist = 'testlist'
        testlistset.add(testlist, ToDo)
        assert testlist in testlistset
        testlistset.remove(testlist)
        assert testlist not in testlistset
        testlistset += (testlist, ToDo)
        assert testlist in testlistset
        testlistset -= testlist
        assert testlist not in testlistset
        testlistset += (testlist, ToDo)
        txtobjfile = testlistset[testlist]
        del testlistset[testlist]
        assert not txtobjfile.path.exists()




unittest.main()


