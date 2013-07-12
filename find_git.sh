#!/bin/bash

LIST_ONLY=0
DIRNAME=0

function help () {
    echo "$1: find git repositories in one or more paths
  USAGE
    $1 [-lb] [paths ...]
  POSITIONAL ARGUMENTS:
    paths    paths in which search for git. Default to \$PWD 
  OPTIONAL ARGUMENTS:
    -l  list only (doesn't display repo status)
    -b  print only git's dirname
"
}

function find_git () {
    find "$1" -type d -name '.git' -prune
}

while getopts "hlbe:" arg
do
    case $arg in
	b) DIRNAME=1
	    ;;
	e) CMD="$OPTARG"
	    ;;
        l)  LIST_ONLY=1
            ;;
        *|h)
            help "$(basename "$0")"
            exit 0
    esac
done
shift $(($OPTIND - 1))

if [ $DIRNAME -eq 1 ]
then
    function _print () {
	basename "$(dirname "$1")"
    }
else
    function _print () {
	echo "$1"
}
fi

if [ $LIST_ONLY -eq 1 ]
then
    function print_out () {
	while read dir_name
	do
	    _print $dir_name
	done
    }
else
    function print_out () {
	while read dir_name
	do
	    cd "$(dirname $dir_name)"
	    if [ -n "$(git status -s)" ]
            then
		echo "C: $(_print "$dir_name")"
	    else
		echo "U: $(_print "$dir_name")"
	    fi
	    cd - &>/dev/null
	done
}
fi

if [ $# -gt 0 ]
then
    for path in "$@"
    do
	find_git "$path" | print_out
    done
else
    find_git "$PWD" | print_out
fi

exit


