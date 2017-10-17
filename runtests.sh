#!/bin/sh

files_with_tests="eb_activity.py eb_cmds_loader.py"

for file in $files_with_tests; do
    echo "Checking $file..."
    python3 -m doctest $file
done
