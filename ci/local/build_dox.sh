#!/bin/sh
set -eu
#
# A simple script to make executing HTML-generation easy
#
###########################################################################

# Navigate into the project content-directory
cd /watchmaker || ( echo "Dir-change failed. Aborting..." ; exit 1 )

# Build watchmaker
uv build

# Install the just-built watchmaker python modules
uv pip install --system ./dist/watchmaker-*.whl

# Build the HTML files
uv run sphinx-build -a -E -W --keep-going -b html docs dist/docs

# Test the documentation
uv run sphinx-build -b doctest docs dist/docs

# Test documentation's link-refs
uv run sphinx-build -b linkcheck docs dist/docs

