#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import sys

class TuringLabJson(object):
    def __init__(self, code, instructions, statistics, filename):
        self.code = code
        self.instructions = instructions
        self.statistics = statistics
        self.filename = filename

    def instr_json(self):
        res = [{"code": {'language': 'python', 'content': l}, "text": i} for
               (l, i) in zip(self.code, self.instructions)]
        turinglab_json = {"title": self.filename.split('/')[-1],
                          "description": "POST EDIT",
                          "image": "POST EDIT",
                          "steps": []
                          }
        for each in res:
            step = {}
            step['title'] = 'POST EDIT'
            step['description'] = 'POST EDIT'
            step['image'] = 'POST EDIT'
            step['components'] = [each]
            turinglab_json['steps'].append(step)

        json.dump(turinglab_json, sys.stdout, indent=4)


    def instr_json2(self):
        res = [{"code": l, "text": i} for (l, i) in
               zip(self.code, self.instructions)]
        turinglab_json = {"name": self.filename.split('/')[-1],
                          "description": "POST EDIT",
                          "steps": []
                          }
        for each in res:
            step = {}
            step['name'] = 'POST EDIT'
            step['description'] = 'POST EDIT'
            step['components'] = [each]
            turinglab_json['steps'].append(step)

        json.dump(turinglab_json, sys.stdout, indent=4)


    def statis_json(self):
        json.dump(self.statistics, sys.stdout, indent=4)
