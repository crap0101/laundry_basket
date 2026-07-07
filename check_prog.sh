#!/bin/bash
#
# author: Marco Chieppa | crap0101
#


function usage () {
    cat <<HELP
DESCRIPTION: use ps to check the given programs
SYNOPSIS: $(basename "$0") [OPTION] [PROGNAME]...
    -h         show this help and exit.
HELP
}

if [ $# -eq 0 ]
then
    usage $0
    exit 1
fi

while getopts "h" arg
do
    case $arg in
        *|h)
	        usage $0
            exit 0
    esac
done
shift $(($OPTIND - 1))


for prog in "$@"; do
    ps -C "$prog" -o comm=,args=
done
