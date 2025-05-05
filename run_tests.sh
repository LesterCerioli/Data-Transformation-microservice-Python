#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -m unittest discover -s tests -p "test_*.py" -v