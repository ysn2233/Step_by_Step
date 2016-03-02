#!/bin/bash
INDIR=sample_inputs
OUTDIR=sample_outputs
CONFIG=.sample_coveragerc

rm -rf $OUTDIR/*
coverage erase --rcfile=$CONFIG
rm -rf sample_htmlcov/*

pyfile=`find $INDIR -name '*.py'`
for pf in $pyfile
do
    bname=`basename $pf`
    coverage run --rcfile=$CONFIG -a unparser.py $pf > $OUTDIR/$bname.txt
done
coverage report --rcfile=$CONFIG
coverage html --rcfile=$CONFIG
