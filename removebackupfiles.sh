#!/bin/bash

function usage ()
{
    echo -ne "$0: remove backup file by suffix.
    USAGE: $0 [-S] [[-s SUFFIX] ...] PATH [PATH ...]
    OPTIONS:
        -s SUFFIX   remove file ending in SUFFIX
        -h          print this help and exit
    NOTE: default suffix pattern is '*~'. Use the -S
          option as *first* to remove this pattern from the list.
"
}

set -o noglob
shopt -u nullglob

SFX=( '-name *~ -o' )

while getopts "Ss:h" arg
do
    case $arg in
	S)
	    SFX=( );;
	s)
	    SFX[${#SFX[@]}]="-name $OPTARG -o";;
        *|h)
            usage
            exit 1;;
    esac
done
shift $((OPTIND-1))

if [ $# -lt 1 -o ${#SFX[@]} -eq 0 ]; then
    usage
    exit 2
fi

SFX[${#SFX[@]}]="-false"

for path in "$@"
do
    find "$path" -type f \( ${SFX[@]} \) -delete
done
