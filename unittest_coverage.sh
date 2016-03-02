#!/bin/bash
INDIR=unittest_inputs
OUTDIR=unittest_outputs
CONFIG=.unittest_coveragerc

rm -rf $OUTDIR/*
coverage erase --rcfile=$CONFIG
rm -rf unittest_htmlcov/*

coverage run --rcfile=$CONFIG -a test_unparser.py
coverage report --rcfile=$CONFIG
coverage html --rcfile=$CONFIG
