#!/bin/bash
#INDIR=unittest_inputs
#OUTDIR=unittest_outputs
CONFIG=.unittest_coveragerc

coverage erase --rcfile=$CONFIG
rm -rf unittest_htmlcov

coverage run --rcfile=$CONFIG --branch -a test_instructor.py
coverage report --rcfile=$CONFIG
coverage html --rcfile=$CONFIG
