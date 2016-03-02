#!/bin/bash
INDIR=sample_inputs

coverage erase
rm -rf htmlcov

coverage run --source=unparser test_unparser.py

coverage report
coverage html

