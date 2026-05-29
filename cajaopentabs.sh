#!/bin/bash

# @author: Marco Chieppa | crap0101
#
# Open tabs in caja reading paths from a file (one per line)
# ignoring lines NOT starting with '/'
# 
# requires: awk|seq, xargs

if [ $# -ne 1 ]; then
    INPUTFILE="~/0.cajaopentabs"
    if [ $# -gt 1 ]; then
	echo "[NOTE] using by default $INPUTFILE ($# args received: $@)"
    else
	echo "[NOTE] using by default $INPUTFILE ($# args received)"
    fi
else
    INPUTFILE="$1"
fi

awk '$1 ~ /^\// {printf "\"%s\" ", $0}' "$INPUTFILE" | xargs caja -t

# or:
#sed -e 's/^\/.*$/\"&\"/g' -e '/^#/d' "$INPUTFILE" | xargs caja -t
