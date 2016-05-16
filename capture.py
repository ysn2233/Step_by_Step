#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import shutil
import sys

TMP_PY = "tmp.py"
TMP_EPS = "tmp.eps"
TMP_PNG = "tmp.png"

def run(fn):
    # copy to tmp.py
    shutil.copyfile(fn, TMP_PY)

    # append capture code
    with open(TMP_PY, 'a') as f:
        f.write('\n')
        f.write('screen = t.getscreen()\n')
        f.write('canvas = screen.getcanvas().postscript(file="%s")' % TMP_EPS);

    # run to capture
    subprocess.call(['python', TMP_PY])

    # convert to png with white background
    args = ['convert', '-flatten', TMP_EPS, '-scale', '800x800', TMP_PNG]
    subprocess.call(args)

    # crop image
    args = ['convert', TMP_PNG, '-fuzz', '%1', '-trim', '+repage', TMP_PNG]
    subprocess.call(args)

    # pad image
    args = ['convert', TMP_PNG, '-gravity', 'center', '-background', 'White',
            '-extent', '250x250', TMP_PNG]
    subprocess.call(args)

    # remove all tmp files
    pass

if __name__ == '__main__':
    run(sys.argv[1])
