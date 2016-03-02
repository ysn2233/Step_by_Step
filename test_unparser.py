import ast
import sys
import mock
import unparser
import unittest
import cStringIO

class TestHelperFunctions(unittest.TestCase):
    def test_leave(self):
        # mock tree and file out coz they are irrelevant in testing leave
        tree = mock.MagicMock()
        file = mock.MagicMock()

        # create an unparser instance and call leave method
        up = unparser.Unparser(tree, file)
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
    def test_factors(self):
        # base name of file, eg "factors" for factors.py and factors.txt
        fn = 'factors'

        # read source code
        with open('sample_inputs/%s.py' % fn, 'r') as in_file:
            code = in_file.read()

        # run unparser and save output to buf
        buf = cStringIO.StringIO()
        tree = ast.parse(code, '<unknown>', 'exec')
        up = unparser.Unparser(tree, buf)
        up.run()

        # read ground truth output
        with open('sample_outputs/%s.txt' % fn, 'r') as sample_out_file:
            sample_output = sample_out_file.read()

        # compare program output with ground truth output
        self.assertEqual(sample_output, buf.getvalue())

    def test_for(self):
        # TODO: TO BE IMPLEMENTED
        pass

    def test_while(self):
        # TODO: TO BE IMPLEMENTED
        pass


if __name__ == '__main__':
    unittest.main()
