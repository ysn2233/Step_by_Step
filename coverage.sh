#!/bin/bash
INDIR=sample_inputs

coverage erase
rm -rf htmlcov

coverage run --source=instructor test_instructor.py

coverage report
coverage html

