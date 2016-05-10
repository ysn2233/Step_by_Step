#!/usr/bin/python
# -*- coding: utf-8 -*-

"Usage: main.py [-n|d] [-l|d] <path to source file>"
import unparse
import instructor
import sys
import ast
import cStringIO
import os
import json

def main(argv):
    if len(argv) < 1:
        print __doc__
        return

    mode = unparse.Mode.normal
    level = unparse.Level.low
    for i in range(len(argv) - 1):
        if argv[i] == "-n":
            mode = unparse.Mode.normal
        elif argv[i] == "-d":
            mode = unparse.Mode.depend
        elif argv[i] == "-l":
            level = unparse.Level.low
        elif argv[i] == "-h":
            level = unparse.Level.high
    fn = argv[-1]

    assert os.path.exists(fn), "File doesn't exist: \"" + fn + "\""
    with open(fn, "r") as f:
        code = f.read()
    tree = ast.parse(code, fn, "exec")
    code_lines = [l for l in unparse.Unparser(tree, mode, level).run()]
    instructions = [i for i in instructor.Unparser(tree, mode, level).run()]

    # TuringLab json - version of 4 May email from Henry
    # res = [{"code": l, "text": i} for (l, i) in
    #        zip(code_lines, instructions)]
    # turinglab_json = {"name": fn.split('/')[-1],
    #                   "description": "POST EDIT",
    #                   "steps": []
    #                   }
    # for each in res:
    #     step = {}
    #     step['name'] = 'POST EDIT'
    #     step['description'] = 'POST EDIT'
    #     step['components'] = each
    #     turinglab_json['steps'].append(step)

    # TuringLab json - version of report 1
    res = [{"code": {'language': 'python', 'content': l}, "text": i} for (l, i)
           in zip(code_lines, instructions)]
    turinglab_json = {"title": fn.split('/')[-1],
                      "description": "POST EDIT",
                      "image": "POST EDIT",
                      "steps": []
                      }
    for each in res:
        step = {}
        step['title'] = 'POST EDIT'
        step['description'] = 'POST EDIT'
        step['image'] = 'POST EDIT'
        step['components'] = each
        turinglab_json['steps'].append(step)


    json.dump(turinglab_json, sys.stdout, indent=4)

if __name__ == '__main__':
    main(sys.argv[1:])
