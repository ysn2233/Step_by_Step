#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import shutil
import sys
import os

TMP_PY = "tmp.py"
TMP_EPS = "tmp.eps"
TMP_PNG = "tmp.png"

def run(fn):
    basename = fn.rsplit('/', 1)[-1][:-2]
    dirpath = fn.rsplit('/', 1)[0]
    TMP_EPS = basename + 'eps'
    TMP_PNG = basename + 'png'

    # remove files of last time
    try:
        os.remove(fn[:-2] + 'png')
        os.remove(fn[:-2] + 'eps')
    except:
        pass

    # copy to tmp.py
    shutil.copyfile(fn, TMP_PY)

    # append capture code
    with open(TMP_PY, 'a') as f:
        f.write('\n')
        f.write('screen = t.getscreen()\n')
        f.write('canvas = screen.getcanvas().postscript(file="%s")' % TMP_EPS);
        f.write('\n')
        f.write('raw_input()')

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
    try:
        os.remove(TMP_PY)
        shutil.move(TMP_PNG, dirpath)
        shutil.move(TMP_EPS, dirpath)
    except:
        pass

if __name__ == '__main__':
    run(sys.argv[1])
