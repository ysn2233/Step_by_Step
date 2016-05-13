#!/bin/bash
INDIR=sample_inputs
OUTDIR=sample_outputs
SAMPLE=draw_house.py
CONFIG=.unittest_coveragerc

coverage erase --rcfile=$CONFIG
rm -rf unittest_htmlcov

coverage run --rcfile=$CONFIG -a test_processor.py
coverage run --rcfile=$CONFIG -a processor.py -l -i $INDIR/$SAMPLE > $OUTDIR/processor_low.txt
coverage run --rcfile=$CONFIG -a processor.py -h -i $INDIR/$SAMPLE > $OUTDIR/processor_high.txt
coverage run --rcfile=$CONFIG -a processor.py -s $INDIR/$SAMPLE > $OUTDIR/processor_statis.txt

coverage run --rcfile=$CONFIG -a reorganiser.py -n $INDIR/$SAMPLE > $OUTDIR/reorganiser_normal.txt
coverage run --rcfile=$CONFIG -a reorganiser.py -d $INDIR/$SAMPLE > $OUTDIR/reorganiser_depend.txt

coverage run --rcfile=$CONFIG -a main.py -n -l -i $INDIR/$SAMPLE > $OUTDIR/main_normal_low.json
coverage run --rcfile=$CONFIG -a main.py -d -l -i $INDIR/$SAMPLE > $OUTDIR/main_depend_low.json
coverage run --rcfile=$CONFIG -a main.py -n -h -i $INDIR/$SAMPLE > $OUTDIR/main_normal_high.json
coverage run --rcfile=$CONFIG -a main.py -d -h -i $INDIR/$SAMPLE > $OUTDIR/main_depend_high.json
coverage run --rcfile=$CONFIG -a main.py -s $INDIR/$SAMPLE > $OUTDIR/main_statis.json

coverage report --rcfile=$CONFIG
coverage html --rcfile=$CONFIG
