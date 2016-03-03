import ast
import sys
import mock
import instructor
import unittest
import cStringIO

class TestHelperFunctions(unittest.TestCase):
    def test_leave(self):
        # mock tree and file out coz they are irrelevant in testing leave
        tree = mock.MagicMock()

        # create an instructor instance and call leave method
        up = instructor.Unparser(tree)
        up.leave()

        # check if result is as expected
        self.assertEqual(up._indent, -1)

    def test_newline(self):
        # TODO: TO BE IMPLEMENTED
        pass

    def test_enter(self):
        # TODO: TO BE IMPLEMENTED
        pass

class TestNode(unittest.TestCase):
    def test_for(self):
        # TODO: TO BE IMPLEMENTED
        pass

    def test_while(self):
        # TODO: TO BE IMPLEMENTED
        pass


if __name__ == '__main__':
    unittest.main()
