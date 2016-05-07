#!/usr/bin/python
# -*- coding: utf-8 -*-

"Usage: main.py [-n|d] <path to source file>"
import unparse
import instructor
import cStringIO
import sys
import ast
import json

def main(args):
    if args[0] == '-n':
        mode = unparse.Mode.normal
        fn = args[1]
    elif args[0] == '-d':
        mode = unparse.Mode.depend
        fn = args[1]
    else:
        mode = unparse.Mode.normal
        fn = args[0]

    with open(fn, "r") as f:
        code = f.read()
    tree = ast.parse(code, fn, "exec")
    code_lines = [l for l in unparse.Unparser(tree, mode).run()]
    instructions = [i for i in instructor.Unparser(tree, mode).run()]

    res = [{"code": l, "text": i} for (l, i) in
           zip(code_lines, instructions)]

    turinglab_json = {"name": fn.split('/')[-1],
                      "description": "POST EDIT",
                      "steps": []
                      }
    for each in res:
        step = {}
        step['name'] = 'POST EDIT'
        step['description'] = 'POST EDIT'
        step['components'] = each
        turinglab_json['steps'].append(step)

    json.dump(turinglab_json, sys.stdout, indent=4)

if __name__ == '__main__':
    main(sys.argv[1:])
