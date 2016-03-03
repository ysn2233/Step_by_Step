#!/usr/bin/python
# -*- coding: utf-8 -*-

import unparse
import instructor
import cStringIO
import sys
import ast
import json

if __name__ == '__main__':
    fn = sys.argv[1]
    with open(fn, 'r') as f:
        code = f.read()

    tree = ast.parse(code, fn, 'exec')
    instructions = [ins for ins in instructor.Unparser(tree).run() if ins]

    src = cStringIO.StringIO()
    unparse.Unparser(tree, src)
    lines = [line for line in src.getvalue().split('\n') if line]

    res = [{'code': code, 'instruction': ins} for (code, ins) in
           zip(lines, instructions)]
    json.dump(res, sys.stdout, indent=4)
