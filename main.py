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
           in zip(steps_code, steps_instructions)]
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
