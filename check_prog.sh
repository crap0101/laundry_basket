#!/bin/bash
#
# author: Marco Chieppa | crap0101
#

if [ $# -lt 1 ]; then
    echo "USAGE: $0 [PROG_NAME ...]"
    exit 1
fi

for prog in "$@"; do
    ps -C "$prog" -o comm=,args=
done
