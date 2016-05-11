#!/usr/bin/python
# -*- coding: utf-8 -*-

"Usage: main.py [-n|d|s] [-l|d] <path to source file>"
import sys
import ast
import cStringIO
import os
import settings

import reorganizer
import unparse
import instructor
from formatter import TuringlabJson

def main(argv):
    if len(argv) < 1:
        print __doc__
        return

    mode = settings.DEPEND
    level = settings.LOW
    stat_only = False
    for i in range(len(argv) - 1):
        if argv[i] == "-n":
            mode = settings.NORMAL
        elif argv[i] == "-d":
            mode = settings.DEPEND
        elif argv[i] == "-l":
            level = settings.LOW
        elif argv[i] == "-h":
            level = settings.HIGH
        elif argv[i] == '-s':
            stat_only = True
    fn = argv[-1]
    assert os.path.exists(fn), "File doesn't exist: \"" + fn + "\""

    # reorganize the syntax tree according to denpendencies
    ordered_tree = reorganizer.Unparser(fn).run()

    # unparse reorganized AST back to code
    steps_code = unparse.Unparser(ordered_tree, lvl=level).run()

    # generate instructions & statistics by analyzing the AST
    steps_instructions, statistics = \
        instructor.Unparser(ordered_tree, mode, level).run()

    # write JSON output
    json = TuringlabJson(steps_code, steps_instructions, statistics, fn)
    if stat_only:
        json.dump_stat()
    else:
        json.report1_json()
    # json.email_json()

if __name__ == '__main__':
    main(sys.argv[1:])
