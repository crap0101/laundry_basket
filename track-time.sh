#!/bin/bash

function usage () {
    cat <<HELP
DESCRIPTION: Print the playing time of the provided media files.
SYNOPSIS: $(basename "$0") [OPTION] [FILE]...
    -i VALUE   force the mediainfo's --Inform template to VALUE.
               Can be any of: Video, Audio, General (default).
    -t         Print also the total time.
    -T         Print only the total time.
    -h         show this help and exit.

REQUIRES: mediainfo, gawk >= 4
HELP
}

INFORM_TYPE="General"
TOTAL_TIME=0
TOTAL_TIME_ONLY=0

if [ $# -eq 0 ]
then
    usage $0
    exit 1
fi

while getopts "i:tTh" arg
do
    case $arg in
        i)  INFORM_TYPE="$OPTARG"
            ;;
	t)  TOTAL_TIME=1
	    ;;
	T)  TOTAL_TIME_ONLY=1
	    TOTAL_TIME=1
	    ;;
        *|h)
	    usage $0
            exit 0
    esac
done
shift $(($OPTIND - 1))

for arg in "$@"
do
    duration=$(mediainfo --Inform="$INFORM_TYPE;%Duration%" "$arg")
    printf "%s\t$(basename "$arg")\n" "$duration"
done | gawk -v print_total=$TOTAL_TIME -v total_only=$TOTAL_TIME_ONLY '
    BEGIN {
        tot_secs = 0
    }
    $1 ~ /[0-9]+/ {
	s = $1 / 1000
	tot_secs += s
        mins += track_m = s / 60
        secs += track_s = s % 60
	$1 = ""
	if (total_only == 0) {
	   printf("%02d:%02d\t%s\n", track_m, track_s, $0)
	}
	next
    }
    {
        printf("ERROR: Malformed time: <%s>\n", $1)
    }
    END {
        if (print_total == 1)
	   printf("Total Time: %02d:%02d\n", tot_secs / 60, tot_secs % 60)
    }'
