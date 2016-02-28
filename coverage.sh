#!/bin/bash
INDIR=sample_inputs
OUTDIR=sample_outputs

rm -rf $OUTDIR
mkdir $OUTDIR
coverage erase
rm -rf htmlcov

pyfile=`find $INDIR -name '*.py'`
for pf in $pyfile
do
    bname=`basename $pf`
    coverage run -a unparser.py $pf > ./$OUTDIR/$bname.txt
done

coverage report
coverage html

