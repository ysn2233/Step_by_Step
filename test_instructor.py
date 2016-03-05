#!/usr/bin/python
# -*- coding: utf-8 -*-

"Usage: test_instructor.py"
import unittest
import cStringIO
import instructor

PY_DIR = "unittest_inputs/"
TXT_DIR = "unittest_outputs/"

class TestInstructor(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestInstructor, self).__init__(*args, **kwargs)
        self.result = [];
        self.expect = [];

    def setUp(self):
        py_filename = PY_DIR + self._testMethodName + ".py"
        buffer = cStringIO.StringIO()
        instructor.roundtrip(py_filename, buffer)
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
    
    def test_augAssign(self):
        self.compare()

    def test_return(self):
        self.compare()

    def test_break(self):
        self.compare()
    
    def test_continue(self):
        self.compare()
    
    def test_assert(self):
        self.compare()
    
    def test_print(self):
        self.compare()
    
    def test_classDef(self):
        self.compare()

    def test_functionDef(self):
        self.compare()

    def test_for(self):
        self.compare()

    def test_if(self):
        self.compare()
    
    def test_while(self):
        self.compare()

    def test_num(self):
        self.compare()

    def test_list(self):
        self.compare()
    
    def test_ifexp(self):
        self.compare()
    
    def test_set(self):
        self.compare()
    
    def test_dict(self):
        self.compare()
    
    def test_tuple(self):
        self.compare()
    
    def test_unaryop(self):
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
