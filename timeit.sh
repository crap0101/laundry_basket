#!/bin/bash
#
# author: Marco Chieppa | crap0101
#

shopt -s extglob

function usage () {
    echo "USAGE: %prog [REPETITIONS] COMMAND
    -h, --help    display this help
"
}

rep=1000

case "$1" in
    -h|--help|"")
	usage
	exit 1;;
    +([0-9]))
        rep=$1
	shift;;
esac

if [[ $# -eq 0 ]]; then
    usage
    exit 1
fi

start=$(date +%s)
for i in $(seq 1 $rep); do
    "$@"
done
end=$(date +%s)

tot=$(expr $end - $start)
/usr/bin/printf "single: %.4f (tot: %.4f)\n" $(bc <<< "scale=4;$tot / $rep") $tot 1>&2
