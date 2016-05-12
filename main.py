#!/usr/bin/python
# -*- coding: utf-8 -*-

"Usage: main.py [-n|d] [-l|d] [-b|i|s] <path to source file>"
import sys
import ast
import cStringIO
import os
import settings

import formatter
import reorganiser
import processor

def main(argv):
    if len(argv) < 1:
        print __doc__
        return

    mode = settings.DEPEND
    level = settings.LOW
    option = settings.BOTH
    for i in range(len(argv) - 1):
        if argv[i] == "-n":
            mode = settings.NORMAL
        elif argv[i] == "-d":
            mode = settings.DEPEND
        elif argv[i] == "-l":
            level = settings.LOW
        elif argv[i] == "-h":
            level = settings.HIGH
        elif argv[i] == "-b":
            option = settings.BOTH
        elif argv[i] == "-i":
            option = settings.INSTR
        elif argv[i] == "-s":
            option = settings.STATIS
        else:
            print __doc__
            return

    filename = argv[-1]
    assert os.path.exists(filename), "File doesn't exist: \"" + filename + "\""
    with open(filename, "r") as pyfile:
        source = pyfile.read()
    tree = compile(source, filename, "exec", ast.PyCF_ONLY_AST)

    # generate re-organised source code
    front_code, back_code = reorganiser.Reorganiser(tree, mode, level).run()

    # generate instructions and statistics
    new_source = "\n".join(back_code)
    new_tree = compile(new_source, filename, "exec", ast.PyCF_ONLY_AST)
    instructions, statistics = processor.Processor(new_tree, level).run()

    # generate JSON files
    turinglab_json = formatter.TuringLabJson(front_code, instructions, statistics, filename)
    if option != settings.STATIS:
        turinglab_json.instr_json()
        # turinglab_json.instr_json2()
    if option != settings.INSTR:
        turinglab_json.statis_json()

if __name__ == '__main__':
    main(sys.argv[1:])
