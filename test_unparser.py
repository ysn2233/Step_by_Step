#!/usr/bin/python
# -*- coding: utf-8 -*-

"Usage: test_unparser.py"
import unittest
import unparser

PY_DIR = "unittest_inputs/"
TXT_DIR = "unittest_outputs/"

MODELS = {
"test_import":
"\nImport the turtle module\n"
}

class TestUnparser(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestUnparser, self).__init__(*args, **kwargs)
        self.result = ""

    def setUp(self):
        py_filename = PY_DIR + self._testMethodName + ".py"
        txt_filename = TXT_DIR + self._testMethodName + ".txt"
        with open(txt_filename, "w") as txt_file:
            unparser.roundtrip(py_filename, txt_file)
        with open(txt_filename, "r") as txt_file:
            self.result = txt_file.read()

    def test_import(self):
        self.assertEqual(self.result, MODELS[self._testMethodName])

if __name__ == '__main__':
    unittest.main()
