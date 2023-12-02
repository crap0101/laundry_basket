#!/bin/bash
#
# author: Marco Chieppa | crap0101
#

LIST_ONLY=0
DIRNAME=0
CHANGED=0

function help () {
    echo "$1: find git repositories in one or more paths
  USAGE
    $1 [-lb] [paths ...]
  POSITIONAL ARGUMENTS:
    paths    paths in which search for git. Default to \$PWD 
  OPTIONAL ARGUMENTS:
    -b  print only git's dirname.
    -c  print only repos changed from the last push.
    -l  list only (doesn't display status).

  Options -blc can be combined to tune output.
"
}

function find_git () {
    find "$1" -type d -name '.git' -prune
}

while getopts "hlcbe:" arg
do
    case $arg in
	b) DIRNAME=1
	   ;;
	c) CHANGED=1
	   ;;
	e) CMD="$OPTARG" # currently unused
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
    function _getd () {
	basename "$(dirname \"$1\")"
    }
else
    function _getd () {
	dirname "$1"
}
fi


function print_out () {
    while read dir_name
    do
	cd "$(dirname $dir_name)"
	if [ -n "$(git status -s)" ]
        then
	    if [ $LIST_ONLY -eq 1 ]
	    then
		_getd "$dir_name"
	    else
		echo "C: $(_getd \"$dir_name\")"
	    fi
	elif [ $CHANGED -eq 0 ]
	then
	    if [ $LIST_ONLY -eq 1 ]
	    then
		_getd "$dir_name"
	    else
		echo "U: $(_getd \"$dir_name\")"
	    fi
	fi
	cd - &>/dev/null
    done
}


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


