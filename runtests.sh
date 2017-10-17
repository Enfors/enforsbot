#!/bin/sh

for file in *.py; do
    echo "Checking $file..."
    python3 -m doctest $file
done
