#!/usr/bin/python
# -*- coding: utf-8 -*-

"Usage: main.py [-n|d] [-l|d] <path to source file>"
import unparse
from formatter import TuringlabJson
import instructor
import sys
import ast
import cStringIO
import os
import settings

def main(argv):
    if len(argv) < 1:
        print __doc__
        return

    mode = settings.DEPEND
    level = settings.LOW
    for i in range(len(argv) - 1):
        if argv[i] == "-n":
            mode = settings.NORMAL
        elif argv[i] == "-d":
            mode = settings.DEPEND
        elif argv[i] == "-l":
            level = settings.LOW
        elif argv[i] == "-h":
            level = settings.HIGH
    fn = argv[-1]
    assert os.path.exists(fn), "File doesn't exist: \"" + fn + "\""

    steps_code, ordered_tree = unparse.Unparser(fn, mode, level).run()
    steps_instructions = instructor.Unparser(ordered_tree, mode, level).run()

    json = TuringlabJson(steps_code, steps_instructions, fn)
    json.report1_json()
    # json.email_json()

if __name__ == '__main__':
    main(sys.argv[1:])
