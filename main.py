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
    lines = [line for line in unparse.Unparser(tree).run() if line]

    res = [{'code': line, 'instruction': ins} for (line, ins) in
           zip(lines, instructions)]
    json.dump(res, sys.stdout, indent=4)
