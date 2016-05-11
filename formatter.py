#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import sys

class TuringlabJson(object):
    def __init__(self, steps_code, steps_instructions, fn):
        self.code = steps_code
        self.instructions = steps_instructions
        self.fn = fn

    def email_json(self):
        res = [{"code": l, "text": i} for (l, i) in
               zip(self.code, self.instructions)]
        turinglab_json = {"name": self.fn.split('/')[-1],
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

    def report1_json(self):
        res = [{"code": {'language': 'python', 'content': l}, "text": i} for
               (l, i) in zip(self.code, self.instructions)]
        turinglab_json = {"title": self.fn.split('/')[-1],
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
