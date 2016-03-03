#!/usr/bin/python
# -*- coding: utf-8 -*-

"Usage: test_unparser.py"
import unittest
import cStringIO
import unparser

PY_DIR = "unittest_inputs/"
TXT_DIR = "unittest_outputs/"

class TestUnparser(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestUnparser, self).__init__(*args, **kwargs)
        self.result = [];
        self.expect = [];

    def setUp(self):
        py_filename = PY_DIR + self._testMethodName + ".py"
        buffer = cStringIO.StringIO()
        unparser.roundtrip(py_filename, buffer)
        self.result = buffer.getvalue().splitlines(True)

        txt_filename = TXT_DIR + self._testMethodName + ".txt"
        with open(txt_filename, "r") as txt_file:
            self.expect = txt_file.read().splitlines(True)

    def compare(self):
        self.assertEqual(len(self.result), len(self.expect))
        for i in range(len(self.result)):
            self.assertEqual(self.result[i], self.expect[i])

    def test_import(self):
        self.compare()

    def test_binop(self):
        self.compare()

    def test_compare(self):
        self.compare()

    def test_boolop(self):
        self.compare()

    def test_call(self):
        self.compare()

    def test_subscript(self):
        self.compare()

if __name__ == '__main__':
    unittest.main()
