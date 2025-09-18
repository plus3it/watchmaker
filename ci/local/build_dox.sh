#!/bin/sh
set -euo pipefail
#
# A simple script to make executing HTML-generation easy
#
###########################################################################

# Navigate into the project content-directory
cd /watchmaker || ( echo "Dir-change failed. Aborting..." ; exit 1 )

# Build watchmaker
python3 -m build

# Install the just-built watchmaker python modules
python3 -m pip install ./dist/watchmaker-*.whl

# Build the HTML files
sphinx-build -a -E -W --keep-going -b html docs dist/docs

# Test the documentation
sphinx-build -b doctest docs dist/docs

# Test documentation's link-refs
sphinx-build -b linkcheck docs dist/docs

